document.addEventListener('DOMContentLoaded', function() {
    const rutInputs = document.querySelectorAll('.rut-input');
    
    rutInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            // Limpiar caracteres no válidos
            this.value = this.value.replace(/[^0-9kK\-\.]/g, '');
            
            // Eliminar formato existente
            let rut = this.value.replace(/\./g, '').replace(/\-/g, '');
            
            // Limitar a 9 caracteres (8 dígitos + 1 DV) - ¡CORRECCIÓN CLAVE!
            if (rut.length > 9) {
                rut = rut.substring(0, 9);
            }
            
            if (rut.length > 1) {
                // Separar cuerpo (máximo 8 dígitos) y DV
                let body = rut.slice(0, -1);
                let dv = rut.slice(-1).toUpperCase();
                
                // Limitar cuerpo a 8 dígitos - ¡ESENCIAL!
                body = body.substring(0, 8);
                
                // Formatear con puntos (de derecha a izquierda)
                let reversed = body.split('').reverse().join('');
                let formatted = '';
                for (let i = 0; i < reversed.length; i++) {
                    if (i > 0 && i % 3 === 0) {
                        formatted = '.' + formatted;
                    }
                    formatted = reversed[i] + formatted;
                }
                
                this.value = formatted + '-' + dv;
            }
        });
        
        // Validar RUT al perder el foco
        input.addEventListener('blur', function() {
            const rut = this.value;
            if (rut && rut.includes('-')) {
                const [body, dv] = rut.split('-');
                const bodyClean = body.replace(/\./g, '');
                
                // Validar longitud exacta (7 u 8 dígitos)
                if (bodyClean.length < 7 || bodyClean.length > 8) {
                    alert("RUT inválido: debe tener 7 u 8 dígitos antes del guión");
                    this.value = '';
                    this.focus();
                    return;
                }
                
                // Validar dígito verificador
                if (!validarDigitoVerificador(bodyClean, dv)) {
                    alert("Dígito verificador inválido");
                    this.focus();
                }
            }
        });
    });
    
    // Función para validar dígito verificador
    function validarDigitoVerificador(cuerpo, dv) {
        const rut = cuerpo;
        let suma = 0;
        let multiplicador = 2;
        
        for (let i = rut.length - 1; i >= 0; i--) {
            suma += parseInt(rut[i]) * multiplicador;
            multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
        }
        
        const resto = suma % 11;
        const dvEsperado = resto === 0 ? '0' : 
                           resto === 1 ? 'K' : 
                           (11 - resto).toString();
        
        return dv.toUpperCase() === dvEsperado;
    }
});