const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry => {
        console.log(entry) 
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        } 
        else {
            entry.target.classList.remove('show');
        }
    }));
});

const hiddenPieces = document.querySelectorAll('.hidden'); 
hiddenPieces.forEach((el) => observer.observe(el));