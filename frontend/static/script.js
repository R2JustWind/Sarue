document.addEventListener("DOMContentLoaded", () => {
  const map = L.map('map').setView([-15.79, -47.89], 12);

  const osm = L.tileLayer(
    'https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

  const satelite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
  );

  L.control.layers(
    {
      "Mapa": osm,
      "Satélite": satelite
    }
  ).addTo(map);

  setTimeout(() => {
    map.invalidateSize();
  }, 300);

  const textarea = document.querySelector("#chat-card textarea");
  const messages = document.getElementById("messages");

  let markers = [];
  let sectorLayers = [];

  function clearMap() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    clearSectors();
  }

  function clearSectors() {
    sectorLayers.forEach(layer => map.removeLayer(layer));
    sectorLayers = [];
  }

  function drawSectorLayer(geojsonFeatures) {
    clearSectors();

    const layer = L.geoJSON(geojsonFeatures, {
      style: {
        color: "#ff0000",
        weight: 2,
        fillOpacity: 0.3
      },

      onEachFeature: function(feature, layer) {
        const props = feature.properties || {};

        layer.bindPopup(`
          <b>Setor:</b> ${props.CD_SETOR || "N/A"}<br>
          <b>Região:</b> ${props.NM_SUBDIST || "N/A"}
        `)
      }
    }).addTo(map);

    sectorLayers.push(layer);

    console.log("GeoJSON adicionado ao mapa:", geojsonFeatures);
    console.log(layer);

    map.fitBounds(layer.getBounds());
  }

 function addMarkers(points) {
  clearMap();

  const bounds = [];

  points.forEach(p => {

    const popupContent = `
      <div style="min-width:180px">
        <b>${p.nome || p.label || "Local"}</b><br>
        <small>Lat: ${p.lat}<br>Lng: ${p.lng}</small><br>
        ${p.endereco ? `<br><small>${p.endereco}</small>` : ""}
        ${p.obs ? `<br><i>${p.obs}</i>` : ""}
      </div>
    `;

    const marker = L.marker([+p.lat, +p.lng])
      .addTo(map)
      .bindPopup(popupContent);

    markers.push(marker);
    bounds.push([+p.lat, +p.lng]);
  });

  if (!bounds.length) return;

  setTimeout(() => {
    map.invalidateSize();

    if (bounds.length === 1) {
      map.setView(bounds[0], 16);
    } else {
      map.fitBounds(bounds, {
        padding: [40, 40],
        maxZoom: 15
      });
    }
  }, 0);
}

  const autoResize = (event) => {
    textarea.style.height = "0px";
    textarea.style.height = textarea.scrollHeight + "px";
  };

  textarea.addEventListener("input", autoResize);
  autoResize();

  textarea.addEventListener("keydown", async (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      const texto = textarea.value.trim();
      if (!texto) return;

      adicionarMensagem("user", texto);
      textarea.value = "";
      autoResize();

      await enviarMensagem(texto);
    }
  });

  function adicionarMensagem(tipo, texto) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("message", tipo);

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = texto;

  wrapper.appendChild(bubble);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

  async function enviarMensagem(texto) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message", "bot");

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.textContent = "Pensando...";

    wrapper.appendChild(bubble);
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;

    try{
      const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type" : "application/json"
      },
      body: JSON.stringify({ message: texto })
    });

    const data = await response.json();
    console.log(data);
    if (data.type === "map_action") {
      if (data.action === "add_markers") {
        addMarkers(data.points);
      }

      if (data.action === "clear_map") {
        clearMap();
        clearSectors();
      }

      if(data.action === "clear_sectors") {
        clearSectors();
      }

      if (data.action === "draw_sector_layer") {
        drawSectorLayer(data.geojson);
      }

      answerEffect(bubble, data.message);
    } else {
      answerEffect(bubble, data.message || data.resposta);
    }
    } catch (error) {
      bubble.textContent = "Erro ao obter resposta do servidor.";
    }
  }

  function answerEffect(element, text, speed = 10) {
    element.textContent = "";
    let i = 0;

    function typing() {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
        messages.scrollTop = messages.scrollHeight;
        setTimeout(typing, speed);
      }
    }
    typing();
  }
});
