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

      const defaultCenter = [33.7756, -84.3963];
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
            marker.bindPopup(labelInput.value || "Pinned location");
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

      const defaultCenter = opts.center || [33.7756, -84.3963];
      const map = L.map(mapEl).setView(defaultCenter, opts.zoom || 11);

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

      if (opts.searchCenter) {
        const centerMarker = L.marker(opts.searchCenter).addTo(map);
        centerMarker.bindPopup("Search center");
        bounds.push(opts.searchCenter);
      }

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

    initSearchRadiusMap: function (opts) {
      const mapEl = ensureMap(opts.mapId);
      if (!mapEl) return null;

      const latInput = document.getElementById(opts.latInputId);
      const lngInput = document.getElementById(opts.lngInputId);
      const radiusInput = document.getElementById(opts.radiusInputId);
      const geolocateBtn = opts.geolocateBtnId ? document.getElementById(opts.geolocateBtnId) : null;
      const statusEl = opts.statusId ? document.getElementById(opts.statusId) : null;

      const map = L.map(mapEl).setView(opts.defaultCenter || [33.7756, -84.3963], opts.zoom || 11);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);

      let resultBounds = [];
      const markers = opts.markers || [];
      markers.forEach(function (m) {
        if (m.lat === null || m.lat === undefined || m.lng === null || m.lng === undefined) {
          return;
        }

        const marker = L.marker([m.lat, m.lng]).addTo(map);
        const popup = makePopupText(m);
        if (popup) marker.bindPopup(popup);
        resultBounds.push([m.lat, m.lng]);
      });

      let centerMarker = null;
      let radiusCircle = null;

      function setStatus(msg) {
        if (statusEl) statusEl.textContent = msg || "";
      }

      function readRadiusMiles() {
        return radiusInput ? parseFloatOrNull(radiusInput.value) : null;
      }

      function updateOverlays(fitMap) {
        const lat = parseFloatOrNull(latInput ? latInput.value : null);
        const lng = parseFloatOrNull(lngInput ? lngInput.value : null);
        const radiusMiles = readRadiusMiles();

        if (centerMarker) {
          map.removeLayer(centerMarker);
          centerMarker = null;
        }
        if (radiusCircle) {
          map.removeLayer(radiusCircle);
          radiusCircle = null;
        }

        const bounds = resultBounds.slice();

        if (lat !== null && lng !== null) {
          centerMarker = L.marker([lat, lng]).addTo(map);
          centerMarker.bindPopup("Search center");
          bounds.push([lat, lng]);

          if (radiusMiles !== null && radiusMiles > 0) {
            radiusCircle = L.circle([lat, lng], {
              radius: milesToMeters(radiusMiles),
            }).addTo(map);
            bounds.push([lat, lng]);
          }
        }

        if (fitMap && bounds.length > 0) {
          map.fitBounds(bounds, { padding: [30, 30] });
        }
      }

      function setSearchCenter(lat, lng, fitMap) {
        if (latInput) latInput.value = lat.toFixed(6);
        if (lngInput) lngInput.value = lng.toFixed(6);
        updateOverlays(fitMap);
      }

      map.on("click", function (e) {
        setSearchCenter(e.latlng.lat, e.latlng.lng, false);
        setStatus("Search center updated from map.");
      });

      if (radiusInput) {
        radiusInput.addEventListener("input", function () {
          updateOverlays(false);
        });
        radiusInput.addEventListener("change", function () {
          updateOverlays(false);
        });
      }

      if (latInput) {
        latInput.addEventListener("change", function () {
          updateOverlays(false);
        });
      }

      if (lngInput) {
        lngInput.addEventListener("change", function () {
          updateOverlays(false);
        });
      }

      if (geolocateBtn) {
        geolocateBtn.addEventListener("click", function () {
          if (!navigator.geolocation) {
            setStatus("Geolocation is not supported in this browser.");
            return;
          }

          setStatus("Getting your location...");

          navigator.geolocation.getCurrentPosition(
            function (pos) {
              const lat = pos.coords.latitude;
              const lng = pos.coords.longitude;
              setSearchCenter(lat, lng, true);
              setStatus("Using your current location.");
            },
            function () {
              setStatus("Could not get your current location.");
            },
            {
              enableHighAccuracy: true,
              timeout: 10000,
              maximumAge: 60000,
            }
          );
        });
      }

      updateOverlays(true);

      if (!latInput.value || !lngInput.value) {
        if (resultBounds.length > 0) {
          map.fitBounds(resultBounds, { padding: [30, 30] });
        }
      }

      setTimeout(function () {
        map.invalidateSize();
      }, 0);

      return {
        map: map,
        setSearchCenter: setSearchCenter,
      };
    },
  };
})();
