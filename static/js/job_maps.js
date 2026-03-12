/* Written by Claude */
(function () {
  function parseFloatOrNull(v) {
    if (v === null || v === undefined || v === "") return null;
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : null;
  }

  function milesToMeters(miles) {
    return miles * 1609.344;
  }

  function makePopupText(marker) {
    if (!marker) return "";
    const parts = [];
    if (marker.title) {
      parts.push(`<div class="fw-bold">${marker.title}</div>`);
    }
    if (marker.subtitle) {
      parts.push(`<div>${marker.subtitle}</div>`);
    }
    if (marker.url) {
      parts.push(`<div class="mt-1"><a href="${marker.url}">Open</a></div>`);
    }
    return parts.join("");
  }

  function ensureMap(elId) {
    const el = document.getElementById(elId);
    if (!el) return null;
    return el;
  }

  window.JobMaps = {
    initSinglePinMap: function (opts) {
      const mapEl = ensureMap(opts.mapId);
      if (!mapEl) return null;

      const latInput = opts.latInputId ? document.getElementById(opts.latInputId) : null;
      const lngInput = opts.lngInputId ? document.getElementById(opts.lngInputId) : null;
      const labelInput = opts.labelInputId ? document.getElementById(opts.labelInputId) : null;

      let lat = latInput ? parseFloatOrNull(latInput.value) : parseFloatOrNull(opts.lat);
      let lng = lngInput ? parseFloatOrNull(lngInput.value) : parseFloatOrNull(opts.lng);

      const defaultCenter = [33.7756, -84.3963]; // Georgia Tech-ish fallback
      const initialZoom = (lat !== null && lng !== null) ? 13 : (opts.initialZoom || 11);

      const map = L.map(mapEl).setView(
        (lat !== null && lng !== null) ? [lat, lng] : defaultCenter,
        initialZoom
      );

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);

      let marker = null;

      function syncInputs(newLat, newLng) {
        if (latInput) latInput.value = newLat.toFixed(6);
        if (lngInput) lngInput.value = newLng.toFixed(6);
      }

      function setMarker(newLat, newLng) {
        if (!marker) {
          marker = L.marker([newLat, newLng], {
            draggable: !!opts.editable,
          }).addTo(map);

          if (opts.editable) {
            marker.on("dragend", function (e) {
              const p = e.target.getLatLng();
              syncInputs(p.lat, p.lng);
            });
          }
        } else {
          marker.setLatLng([newLat, newLng]);
        }

        if (labelInput && labelInput.value) {
          marker.bindPopup(labelInput.value);
        }

        map.panTo([newLat, newLng]);
      }

      if (lat !== null && lng !== null) {
        setMarker(lat, lng);
      }

      if (opts.editable) {
        map.on("click", function (e) {
          setMarker(e.latlng.lat, e.latlng.lng);
          syncInputs(e.latlng.lat, e.latlng.lng);
        });
      }

      function refreshFromInputs() {
        const ilat = latInput ? parseFloatOrNull(latInput.value) : null;
        const ilng = lngInput ? parseFloatOrNull(lngInput.value) : null;
        if (ilat !== null && ilng !== null) {
          setMarker(ilat, ilng);
        }
      }

      if (latInput) latInput.addEventListener("change", refreshFromInputs);
      if (lngInput) lngInput.addEventListener("change", refreshFromInputs);

      if (labelInput) {
        labelInput.addEventListener("input", function () {
          if (marker) {
            const val = labelInput.value || "Pinned location";
            marker.bindPopup(val);
          }
        });
      }

      setTimeout(function () {
        map.invalidateSize();
      }, 0);

      return map;
    },

    initMarkersMap: function (opts) {
      const mapEl = ensureMap(opts.mapId);
      if (!mapEl) return null;

      const map = L.map(mapEl).setView(opts.center || [33.7756, -84.3963], opts.zoom || 11);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);

      const bounds = [];
      const markers = opts.markers || [];

      markers.forEach(function (m) {
        if (m.lat === null || m.lat === undefined || m.lng === null || m.lng === undefined) {
          return;
        }

        const marker = L.marker([m.lat, m.lng]).addTo(map);
        const popup = makePopupText(m);
        if (popup) marker.bindPopup(popup);
        bounds.push([m.lat, m.lng]);
      });

      if (opts.radiusCenter && opts.radiusMiles) {
        L.circle(opts.radiusCenter, {
          radius: milesToMeters(opts.radiusMiles),
        }).addTo(map);
        bounds.push(opts.radiusCenter);
      }

      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [30, 30] });
      }

      setTimeout(function () {
        map.invalidateSize();
      }, 0);

      return map;
    },
  };
})();
