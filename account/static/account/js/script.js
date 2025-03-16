  const inputs = document.querySelectorAll('.w3-input');
  inputs.forEach(input => {
    input.addEventListener('input', function () {
      if (this.classList.contains('input-error')) {
        this.classList.remove('input-error');
      }
    });
  });