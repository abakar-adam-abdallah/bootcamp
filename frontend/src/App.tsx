import { useState } from "react";
import "./App.css";

type Player = { id: string; name: string; balance: number; active: boolean };

export default function App() {
  
  const [players, setPlayers] = useState<Player[]>([]);
  const [name, setName] = useState("");
  const [balance, setBalance] = useState<number>(100);

  
  const uid = () => Math.random().toString(36).slice(2, 9);

  // ajouter un joueur (validation très simple)
  function addPlayer() {
    if (name.trim().length < 2) return alert("Le nom doit faire au moins 2 caractères.");
    if (balance < 0) return alert("Le solde doit être positif.");
    const p: Player = { id: uid(), name: name.trim(), balance, active: false };
    setPlayers((list) => [...list, p]);
    setName("");
    setBalance(100);
  }

  // sélectionner 
  function selectPlayer(id: string) {
    setPlayers((list) => list.map(p => ({ ...p, active: p.id === id })));
  }

  // créditer/débiter
  function changeBalance(id: string, amount: number) {
    setPlayers((list) =>
      list.map(p => p.id === id ? { ...p, balance: Math.max(0, p.balance + amount) } : p)
    );
  }

  // supprimer
  function removePlayer(id: string) {
    setPlayers((list) => list.filter(p => p.id !== id));
  }

  // total (calcul simple)
  const total = players.reduce((s, p) => s + p.balance, 0);

  return (
    <main style={{ padding: 16, maxWidth: 720, margin: "0 auto", display: "grid", gap: 16 }}>
      <h1>👤 Gestion des joueurs (version débutant)</h1>

      {/* Formulaire TRÈS simple */}
      <section style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <input
          placeholder="Nom du joueur"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="number"
          step="1"
          value={balance}
          onChange={(e) => setBalance(Number(e.target.value))}
        />
        <button onClick={addPlayer}>Ajouter</button>
      </section>

      {/* Résumé */}
      <section>
        <strong>Nombre de joueurs : {players.length}</strong> — Total banques : {total} 🪙
      </section>

      {/* Liste des joueurs */}
      <section style={{ display: "grid", gap: 12 }}>
        {players.map((p) => (
          <div
            key={p.id}
            style={{
              border: p.active ? "2px solid #10b981" : "1px solid #ddd",
              borderRadius: 12,
              padding: 12,
              display: "grid",
              gap: 8,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <strong>{p.name} {p.active && "⭐"}</strong>
              <span>Solde : {p.balance} 🪙</span>
            </div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button onClick={() => selectPlayer(p.id)}>Sélectionner</button>
              <button onClick={() => changeBalance(p.id, +10)}>+10</button>
              <button onClick={() => changeBalance(p.id, -10)}>-10</button>
              <button onClick={() => removePlayer(p.id)} style={{ color: "#b91c1c" }}>
                Supprimer
              </button>
            </div>
          </div>
        ))}

        {players.length === 0 && <em>Aucun joueur pour l’instant. Ajoute-en un ci-dessus.</em>}
      </section>
    </main>
  );
}
