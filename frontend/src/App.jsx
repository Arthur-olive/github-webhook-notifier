import React, { useEffect, useState } from "react";

export default function App() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:8000/events")
        .then(res => res.json())
        .then(data => setEvents(data))
        .catch(err => console.error("Erro ao buscar eventos:", err));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "2rem", color: "white", fontFamily: "Arial" }}>
      <h1>Webhook GitHub – Eventos Recebidos</h1>

      {events.length === 0 && (
        <p>Nenhum evento recebido ainda.</p>
      )}

      {events.map((item, idx) => (
        <div
          key={idx}
          style={{
            marginTop: "1rem",
            padding: "1rem",
            border: "1px solid #444",
            background: "#1e1e1e",
            borderRadius: "8px"
          }}
        >
          <h3>Evento: {item.event}</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {JSON.stringify(item.payload, null, 2)}
          </pre>
        </div>
      ))}
    </div>
  );
}
