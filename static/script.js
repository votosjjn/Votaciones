// Splash once per session: shows on first load; hides after 3s
document.addEventListener("DOMContentLoaded", ()=> {
  const splash = document.getElementById("splash-screen");
  if (!sessionStorage.getItem("seen_splash")) {
    sessionStorage.setItem("seen_splash", "1");
    // splash leaves by CSS animation (3s)
  } else {
    if (splash) splash.style.display = "none";
  }
});

function startVoting(nivel){
  const docInput = document.getElementById("doc");
  const msg = document.getElementById("msg");
  msg.textContent = "";
  if (!docInput) return;
  const doc = docInput.value.trim();
  if (!doc) { msg.textContent = "Ingresa tu número de documento."; return; }

  // show vote section
  document.getElementById('home').classList.add('hidden');
  document.getElementById('vote').classList.remove('hidden');
}

function castVote(nivel, candidatoId){
  const doc = document.getElementById("doc").value.trim();
  if (!doc) return alert("Documento requerido.");
  fetch(`/${nivel}/vote`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc: doc, candidato: candidatoId })
  }).then(res => res.json())
    .then(j => {
      if (j.ok) {
        try {
          const bell = new Audio("/static/sonido.mp3");
          bell.play();
        } catch(e){}
        alert("✅ Voto registrado. Gracias por participar.");
        setTimeout(()=> location.reload(), 800);
      } else {
        alert("⚠️ " + (j.msg || "Error al votar"));
      }
    }).catch(err => {
      console.error(err);
      alert("Error de conexión.");
    });
}
