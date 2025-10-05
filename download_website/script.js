const programs = [
    {
        name: "Total Installer",
        description: "Complete installer from strombackfamily.com",
        icon: "assets/images/total_installer.png",
        file: "assets/downloads/total_installer.exe"
    }
];

const container = document.getElementById('programs-container');

programs.forEach(program => {
    const card = document.createElement('div');
    card.classList.add('program-card');
    card.dataset.name = program.name.toLowerCase();

    card.innerHTML = `
        <img src="${program.icon}" alt="${program.name}">
        <h3>${program.name}</h3>
        <p>${program.description}</p>
        <button onclick="downloadProgram('${program.file}')">Download</button>
    `;
    container.appendChild(card);
});

// Search filter
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', () => {
    const filter = searchInput.value.toLowerCase();
    document.querySelectorAll('.program-card').forEach(card => {
        const name = card.dataset.name;
        card.style.display = name.includes(filter) ? 'block' : 'none';
    });
});

function downloadProgram(file) {
    window.location.href = file;
}
