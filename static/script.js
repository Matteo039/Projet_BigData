document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("graphique").getContext("2d");
    let chart;

    const loadingMessage = document.getElementById("loading");

    const fetchData = (periode) => {
        return new Promise((resolve, reject) => {
            setTimeout(() => { // Simulation de délai
                const data = {
                    jour: { labels: ["00h", "01h", "02h", "03h", "04h"], values: [16.25, 13.75, 11.25, 7.75, 8.25] },
                    mois: { labels: ["1", "2", "3", "4", "5"], values: [10, 12, 14, 9, 11] },
                    annee: { labels: ["Jan", "Fév", "Mar", "Avr", "Mai"], values: [12, 14, 13, 15, 11] },
                    historique: { labels: ["1990", "2000", "2010", "2020"], values: [20, 18, 15, 10] }
                };

                // On simule un échec de récupération de données avec une probabilité de 10% pour afficher une erreur
                if (Math.random() < 0.1) {
                    reject("Erreur lors du chargement des données");
                } else {
                    resolve(data[periode] || data.jour);
                }
            }, 1500); // Simule un temps de chargement de 1.5s
        });
    };

    const updateChart = async (periode) => {
        loadingMessage.style.display = "block"; // Afficher "Chargement..."

        try {
            const { labels, values } = await fetchData(periode);
            loadingMessage.style.display = "none"; // Cacher "Chargement..."

            if (chart) chart.destroy(); // Supprimer l'ancien graphique avant d'en créer un nouveau

            chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels,
                    datasets: [{
                        label: `Niveau de pollution PM2.5 (µg/m³) - ${periode}`, // Titre dynamique
                        data: values,
                        borderColor: "blue",
                        backgroundColor: "rgba(0, 0, 255, 0.2)",
                        fill: true
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: true, // Activer l'affichage de la légende
                            position: "top"
                        }
                    }
                }
            });
        } catch (error) {
            loadingMessage.style.display = "none"; // Cacher "Chargement..."
            alert(error); // Afficher une alerte en cas d'erreur
        }
    };

    document.getElementById("periode").addEventListener("change", (e) => {
        updateChart(e.target.value);
    });

    // Charger les données par défaut (au démarrage, période "jour")
    updateChart("jour");
});
