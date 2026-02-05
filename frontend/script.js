document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM carregado");

  const map = L.map("map").setView([-15.79, -47.88], 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);

  setTimeout(() => {
    map.invalidateSize();
  }, 300);

  const textarea = document.querySelector("#chat-card textarea");
  const messages = document.getElementById("messages");

  let markers = [];

  function clearMap() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
  }

 function addMarkers(points) {
  clearMap();

  const bounds = [];

  points.forEach(p => {
    const marker = L.marker([+p.lat, +p.lng])
      .addTo(map)
      .bindPopup(p.label);

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
    if (data.type === "map_action") {
      if (data.action === "add_markers") {
        addMarkers(data.points);
      }

      if (data.action === "clear_map") {
        clearMap();
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
