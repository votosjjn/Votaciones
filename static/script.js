// Splash show once per session
document.addEventListener("DOMContentLoaded", () => {
  const splash = document.getElementById("splash-screen");
  if (!sessionStorage.getItem("seen_splash")) {
    sessionStorage.setItem("seen_splash", "1");
    setTimeout(() => { if (splash) splash.style.display = "none"; }, 2500);
  } else {
    if (splash) splash.style.display = "none";
  }

  // admin trigger (double-click on title)
  const title = document.getElementById("school-title");
  if (title) {
    title.addEventListener("dblclick", () => {
      window.location.href = "/admin";
    });
  }
});

// cast vote called from candidates page
function castVote(nivel, candidato, doc) {
    fetch(`/vote/${nivel}`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({doc: doc, candidato: candidato})
    })
    .then(res => res.json().then(data => ({status: res.status, body: data})))
    .then(({status, body}) => {
        if (body.ok) {
            // Voto exitoso
            window.location.href = "/gracias";
        } else {
            // Redirige a error.html con mensaje
            const mensaje = encodeURIComponent(body.msg || "No se pudo procesar el voto");
            window.location.href = `/error?mensaje=${mensaje}`;
        }
    })
    .catch(err => {
        console.error(err);
        const mensaje = encodeURIComponent("Ocurrió un error al enviar tu voto. Intenta nuevamente.");
        window.location.href = `/error?mensaje=${mensaje}`;
    });
}
