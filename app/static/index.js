console.log('Hello World!');

const input = document.getElementById("message-input");
const btn = document.getElementById("btn-send");
const response_ui = document.getElementById("message-response");
const responseContainer = document.getElementById("response-container");

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        send();
    }
});

btn.addEventListener("click", function() {
    send();
});

function send() {
    const userMessage = input.value;
    if (userMessage.trim() === "") {
        return; // Evita enviar una pregunta vacía
    }
    displayUserMessage(userMessage); // Muestra el mensaje del usuario en el contenedor
    const prompt = {
        prompt: userMessage,
        stream: true
    };
    sendMessage(prompt);
    input.value = ""; // Limpia el campo de entrada después de enviar el mensaje
}

function sendMessage(data) {
    fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Inicio del stream');
        const reader = response.body.getReader();
        let accumulatedText = ''; // Acumula el texto completo

        return new ReadableStream({
            start(controller) {
                function push() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            console.log('Fin del stream');
                            controller.close();

                            // Crea el párrafo con el texto completo
                            const paragraph = document.createElement("p");
                            paragraph.textContent = accumulatedText;
                            responseContainer.appendChild(paragraph);
                            paragraph.classList.add("ia-message");

                            return;
                        }
                        
                        const text = new TextDecoder().decode(value);
                        console.log(text);
                        
                        // Acumula el texto
                        accumulatedText += text;

                        push();
                    });
                }
                push();
            }
        });
    })
    .catch(err => {
        console.error('Error:', err);
    });
}

function displayUserMessage(message) {
    const userParagraph = document.createElement("p");
    userParagraph.textContent = message;
    userParagraph.classList.add("user-message");
    responseContainer.appendChild(userParagraph);
}

const slider = document.getElementById("slider");
const temperatureValue = document.getElementById("temperature-value");

slider.addEventListener("input", function() {
  temperatureValue.textContent = slider.value;
});
