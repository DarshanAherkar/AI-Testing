const tabs = document.querySelectorAll('.tab');
const forms = document.querySelectorAll('.auth-form');

for (const tab of tabs) {
  tab.addEventListener('click', () => {
    const target = tab.dataset.form;

    tabs.forEach((btn) => btn.classList.remove('active'));
    forms.forEach((form) => form.classList.remove('active'));

    tab.classList.add('active');
    document.getElementById(`${target}Form`).classList.add('active');
  });
}

for (const form of forms) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const title = form.querySelector('h2').textContent;
    alert(`${title} successful! Welcome to Darshan Testing.`);
    form.reset();
  });
}
