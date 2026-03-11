const { neon } = require('@neondatabase/serverless');

// Configuration de l'agent Antigravity
const AGENT_NAME = "antigravity";
const DB_URL = "postgresql://neondb_owner:npg_4YpH9BMwmaCX@ep-plain-cell-ady4nccj-pooler.c-2.us-east-1.aws.neon.tech/neondb";

async function antigravityDaemon() {
  const sql = neon(DB_URL);
  
  console.log(`\n🤖 [ANTIGRAVITY DAEMON] Démarré...`);
  console.log(`🛰️  En attente de tâches sur le Nexus Hub...\n`);

  // Boucle de surveillance
  setInterval(async () => {
    try {
      // 1. Je cherche des tâches "pending" ou "in_progress"
      const tasks = await sql`
        SELECT t.id, t.label, t.skill, m.title as mission_title
        FROM tasks t
        JOIN missions m ON t.mission_id = m.id
        WHERE t.status = 'pending'
        LIMIT 1
      `;

      if (tasks.length > 0) {
        const task = tasks[0];
        console.log(`\n📥 REÇU : "${task.label}"`);
        console.log(`📌 Mission : ${task.mission_title}`);
        console.log(`🛠️  Skill requis : ${task.skill}`);

        // 2. Je simule l'exécution
        console.log(`⚙️  L'agent ${AGENT_NAME} analyse la requête...`);
        
        // 3. Je mets à jour le statut en "running" sur ton dashboard
        await sql`UPDATE tasks SET status = 'running' WHERE id = ${task.id}`;
        console.log(`📡 Statut mis à jour sur le HUB : [RUNNING]`);

        // Simulation de travail...
        setTimeout(async () => {
          // 4. Mission accomplie
          await sql`UPDATE tasks SET status = 'done' WHERE id = ${task.id}`;
          console.log(`✅ Tâche terminée : ${task.label}`);
          console.log(`🛰️  Retour en standby...`);
        }, 5000);
      }
    } catch (err) {
      // Erreur silencieuse pour le polling
    }
  }, 3000); // Je vérifie toutes les 3 secondes
}

antigravityDaemon();
