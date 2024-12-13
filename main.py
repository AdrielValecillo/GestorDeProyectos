from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import os
import dotenv
import google.generativeai as genai
import html
from db.db import engine, SessionLocal
import db.models
import db.crud as crud

dotenv.load_dotenv()


db.models.Base.metadata.create_all(bind=engine)


app = FastAPI()



genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 0.1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [ 
        """actua como un ingeriero de software. a partir de un pront que te voy a dar dame una lista 
        de 4 alternativas de solucion del problema a solucionar. lista de 4 alternativas con descripcion 
        de la alternativa y aspectos importantes""",
      ],
    },
    {
      "role": "model",
      "parts": [
        """¡Por supuesto!  Estoy listo para ayudarte a generar alternativas de solución. Por favor, 
        dime cuál es el problema que necesitas resolver. Mientras más detalles me proporciones 
        sobre el problema, como su contexto, restricciones, y objetivos, mejor podré ayudarte a encontrar 
        soluciones viables. **Ejemplo:**"Necesito optimizar el rendimiento de una aplicación 
        web que se ha vuelto lenta.**Respuesta:****1.  Optimizar el código:**    
        * **Descripción:** Revisar el código de la aplicación para identificar áreas de mejora en la eficiencia. 
        Esto podría incluir:       * Eliminar código redundante o ineficiente.        
        * Implementar algoritmos más eficientes.       * Utilizar cachés para almacenar datos que se utilizan con frecuencia.    
        * **Aspectos importantes:** Requiere un profundo conocimiento del código de la aplicación. 
        **2.  Escalar la infraestructura:**   * **Descripción:** Aumentar los recursos del servidor, como la memoria, 
        el procesador o el almacenamiento, para mejorar la capacidad de procesamiento de la aplicación.   
        * **Aspectos importantes:** Puede ser costoso y requiere la configuración de la infraestructura.
        **3.  Implementar una base de datos más eficiente:**   * **Descripción:** Cambiar la base de datos actual por 
        una que sea más eficiente para el tipo de datos y operaciones de la aplicación. 
             * **Aspectos importantes:** Requiere migración de datos y puede tener un impacto en la funcionalidad de la aplicación.
             **4.  Optimizar la consulta a la base de datos:**  
               * **Descripción:** Optimizar las consultas a la base de datos para que sean más eficientes. Esto podría incluir: 
                     * Usar índices para mejorar la búsqueda de datos.  * Evitar consultas complejas que requieran mucho tiempo de procesamiento. 
                         * **Aspectos importantes:** Requiere conocimiento de la base de datos y las consultas SQL.
                         **¡Por favor, dime el problema y te ayudaré a generar alternativas!**""",
      ],
    },
  ]
)


def formatear_mensaje(mensaje: str) -> str:
    mensaje_escapado = html.escape(mensaje)  # Escapa caracteres especiales
    mensaje_formateado = mensaje_escapado.replace("\n", "<br>")
    mensaje2 = mensaje_formateado.replace('*',' ')  # Reemplaza saltos de línea con <br>
    return mensaje2

@app.get("/", response_class=HTMLResponse)
async def formulario():
    formulario_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Escribe tu problema para recibir alternativas de solución</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            color: #333;
        }
        form {
            max-width: 600px;
            margin: auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Describe tu problema detalladamente para recibir alternativas de solución</h1>
    <form action="/chat" method="post">
        <label for="message">Mensaje:</label>
        <textarea id="message" name="message" placeholder="Escribe tu problema aquí..."></textarea>
        <br>
        <input type="submit" value="Generar">
    </form>
</body>
</html>

    """
    return HTMLResponse(content=formulario_html)

# Endpoint para manejar el mensaje enviado desde el formulario
@app.post("/chat", response_class=HTMLResponse)
def chat(message: str = Form(...)):
    response = chat_session.send_message(message)
    
    
    
    # Formatear la respuesta del chat
    respuesta_formateada = formatear_mensaje(response.text)
    
    db = SessionLocal()
    crud.guardar_propuesta(db, message, response.text)

    respuesta_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Respuesta del Chat</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }}
            h1 {{
                color: #333;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                padding: 20px;
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .response {{
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
                color: #333;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                color: #fff;
                background-color: #007bff;
                border: none;
                border-radius: 5px;
                text-decoration: none;
                text-align: center;
            }}
            .button:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Respuesta del Chat</h1>
            <div class="response">
                {respuesta_formateada}
            </div>
            <a href="/" class="button">Volver al formulario</a>
            <a href="/cuadro" class="button" target="_blank">Ir A Generar Tabla de Alternativas</a>
        </div>
    </body>
    </html>
        """
    
    return HTMLResponse(content=respuesta_html)



@app.get("/cuadro", response_class=HTMLResponse)
def get_form():
    html_text = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Propuestas de Alternativas</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: auto;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
        }
        .highlight {
            background-color: #d4edda;
            color: #155724;
        }
        .form-container {
            margin-bottom: 20px;
        }
        .form-container input {
            padding: 10px;
            margin: 5px 0;
            width: calc(100% - 22px);
        }
        .form-container button {
            padding: 10px 20px;
            font-size: 16px;
            color: #fff;
            background-color: #007bff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .form-container button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Evaluación de Alternativas</h1>
        <div class="form-container">
            <h2>Agregar Alternativa</h2>
            <form id="proposalForm">
                <label for="proposal">Alternativa:</label>
                <input type="text" id="proposal" name="proposal" placeholder="Nombre de la Alternativa" required>
                <div id="criteriaInputs">
                    <label for="criteria1">Costo:</label>
                    <input type="number" id="criteria1" name="criteria1" placeholder="Valor del criterio Costo" min="1" max="10" required>
                    <input type="hidden" id="criteriaName1" name="criteriaName1" value="Costo">
                    
                    <label for="criteria2">Eficiencia:</label>
                    <input type="number" id="criteria2" name="criteria2" placeholder="Valor del criterio Eficiencia" min="1" max="10" required>
                    <input type="hidden" id="criteriaName2" name="criteriaName2" value="Eficiencia">
                    
                    <label for="criteria3">Facilidad de Implementación:</label>
                    <input type="number" id="criteria3" name="criteria3" placeholder="Valor del criterio Facilidad de Implementación" min="1" max="10" required>
                    <input type="hidden" id="criteriaName3" name="criteriaName3" value="Facilidad de Implementación">
                    
                    <label for="criteria4">Tiempo:</label>
                    <input type="number" id="criteria4" name="criteria4" placeholder="Valor del criterio Tiempo" min="1" max="10" required>
                    <input type="hidden" id="criteriaName4" name="criteriaName4" value="Tiempo">
                </div>
                <button type="button" onclick="addProposal()">Agregar Alternativa</button>
            </form>
        </div>

        <table id="proposalsTable">
            <thead>
                <tr>
                    <th>Alternativa</th>
                    <th>Costo</th>
                    <th>Eficiencia</th>
                    <th>Facilidad de Implementación</th>
                    <th>Tiempo</th>
                    <th>Total</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
                <!-- Las filas se agregarán aquí dinámicamente -->
            </tbody>
        </table>
    </div>

    <script>
        const criteriaCount = 4;

        function addProposal() {
            const proposal = document.getElementById('proposal').value;
            const criteriaValues = [];
            let total = 0;

            for (let i = 1; i <= criteriaCount; i++) {
                const criteriaValue = parseFloat(document.getElementById(`criteria${i}`).value) || 0;
                if (criteriaValue < 1 || criteriaValue > 10) {
                    alert('Por favor, complete todos los campos correctamente con valores entre 1 y 10.');
                    return;
                }
                criteriaValues.push(criteriaValue);
                total += criteriaValue;
            }

            if (!proposal) {
                alert('Por favor, complete todos los campos correctamente.');
                return;
            }

            const tableBody = document.querySelector('#proposalsTable tbody');
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${proposal}</td>
                ${criteriaValues.map(value => `<td>${value}</td>`).join('')}
                <td class="total">${total}</td>
                <td>
                    <form action="/detalle" method="post" target="_blank">
                        <input type="hidden" name="proposal" value="${proposal}">
                        ${criteriaValues.map((value, index) => `<input type="hidden" name="criteria${index + 1}" value="${value}">`).join('')}
                        <button type="submit">Detalles</button>
                    </form>
                </td>
            `;
            tableBody.appendChild(row);

            highlightMaxTotal();

            // Limpiar campos
            document.getElementById('proposalForm').reset();
        }

        function highlightMaxTotal() {
            const rows = document.querySelectorAll('#proposalsTable tbody tr');
            let maxTotal = -Infinity;
            let maxTotalRow;

            rows.forEach(row => {
                const totalCell = row.querySelector('.total');
                const total = parseFloat(totalCell.textContent);
                if (total > maxTotal) {
                    maxTotal = total;
                    maxTotalRow = row;
                }
            });

            rows.forEach(row => row.querySelector('.total').classList.remove('highlight'));
            if (maxTotalRow) {
                maxTotalRow.querySelector('.total').classList.add('highlight');
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_text)


"""

    db = SessionLocal()
    id_proyectos = crud.obtener_ultima_propuesta(db)
    id_proyecto = id_proyectos.id_proyecto

    
    costo = criteria_values["criteria1"]
    eficiencia = criteria_values["criteria2"]
    facilidad_implementacion = criteria_values["criteria3"]
    tiempo = criteria_values["criteria4"]

    crud.guardar_alternativa(db, id_proyecto, proposal, costo, eficiencia, facilidad_implementacion, tiempo)
"""


@app.post("/detalle", response_class=HTMLResponse)
async def detalle_propuesta(request: Request):
    form_data = await request.form()

    proposal = form_data.get("proposal")

    db = SessionLocal()
    id_proyectos = crud.obtener_ultima_propuesta(db)
    id_proyecto = id_proyectos.id_proyecto

    #crud.guardar_alternativa(db, id_proyecto, proposal)

    criteria_names = {
        "criteria1": "Costo",
        "criteria2": "Eficiencia",
        "criteria3": "Facilidad de Implementación",
        "criteria4": "Tiempo"
    }

    criteria_values = {key: form_data.get(key) for key in criteria_names.keys()}

    costo = criteria_values["criteria1"]
    eficiencia = criteria_values["criteria2"]
    facilidad_implementacion = criteria_values["criteria3"]
    tiempo = criteria_values["criteria4"]

    crud.guardar_alternativa(db, id_proyecto, proposal, costo, eficiencia, facilidad_implementacion, tiempo)

    html_text = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Detalles de la Propuesta</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                padding: 20px;
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            button {{
                padding: 10px 20px;
                font-size: 16px;
                color: #fff;
                background-color: #007bff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            
            textarea {{
                width: 100%;
                height: 150px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            .form-container input, .form-container textarea {{
                padding: 10px;
                margin: 5px 0;
                width: calc(100% - 22px);
            }}
            .form-container button {{
                padding: 10px 20px;
                font-size: 16px;
                color: #fff;
                background-color: #007bff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            .form-container button:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Detalles de la Alternativa</h1>
            <p><strong>Alternativa:</strong> {proposal}</p>
            <p><strong>Descripción de por qué se eligió esta alternativa:</strong></p>
            <textarea id="description" name="description" rows="4" placeholder="Escriba aquí la descripción de por qué se eligió esta alternativa" required></textarea>
    """

    for index, (criteria_key, criteria_value) in enumerate(criteria_values.items(), start=1):
        criterion_name = criteria_names[criteria_key]
        
        html_text += f"""
            <p><strong>{criterion_name}:</strong> Valor Asignado: {criteria_value}</p>
            <br>
            <label for="argumentacion{index}">Argumentación para {criterion_name}:</label>
            <br>
            <textarea id="argumentacion{index}" name="argumentacion{index}" rows="4" placeholder="Escriba la argumentación para el valor del {criterion_name}"></textarea>
            <br>
        """

    html_text += """
            <button onclick="generateSummary()">Generar Vista de Resumen</button>
        </div>
        <script>
            function generateSummary() {
                const proposal = encodeURIComponent(document.querySelector('p strong').textContent);
                const description = encodeURIComponent(document.getElementById('description').value);
                const arguments = Array.from(document.querySelectorAll('textarea[name^=argumentacion]'))
                    .map(textarea => `${textarea.name}=${encodeURIComponent(textarea.value)}`)
                    .join('&');

                const url = `/resumen?proposal=${proposal}&description=${description}&${arguments}`;
                window.open(url, '_blank');
            }
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_text)




@app.get("/resumen", response_class=HTMLResponse)
async def vista_resumen(request: Request):
    query_params = request.query_params

    proposal = query_params.get("proposal", "No disponible")
    description = query_params.get("description", "No disponible")

    criteria_names = {
        "criteria1": "Costo",
        "criteria2": "Eficiencia",
        "criteria3": "Facilidad de Implementación",
        "criteria4": "Tiempo"
    }

    print(description)
    # Filtramos todos los parámetros que empiezan con 'argumentacion'
    arguments = {key: value for key, value in query_params.items() if key.startswith("argumentacion")}

    print(arguments)

    argumentacion_costo = arguments["argumentacion1"]
    argumentacion_eficiencia = arguments["argumentacion2"]
    argumentacion_facilidad = arguments["argumentacion3"]
    argumentacion_tiempo = arguments["argumentacion4"]

    

    db = SessionLocal()
    alternativas = crud.obtener_ulima_alternativa(db)
    print(alternativas.nombre_alternativa)

    propuesta = crud.obtener_propuesta(db, alternativas.id_proyecto)

    print(propuesta.descripcion)

    crud.guardar_argumentacion(db, alternativas.id_alternativa, description, argumentacion_costo, argumentacion_eficiencia, argumentacion_facilidad, argumentacion_tiempo)


    html_text = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vista de Resumen</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }}

            a.button {{
                display: inline-block;
                padding: 10px 20px;
                margin-top: 20px;
                background-color: #007bff;
                color: white;
                text-align: center;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s ease;
            }}

            a.button:hover {{
                background-color: #0056b3;
            }}

            .container {{
                max-width: 600px;
                margin: auto;
                padding: 20px;
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .container p {{
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Vista de Resumen De La Alternativa de la Propuesta</h1>
            <p><strong>Propuesta: </strong> {propuesta.descripcion}</p>
            <br>
            <p><strong>Nombre de la Alternativa:</strong> {alternativas.nombre_alternativa}</p>
            <p><strong>Descripción de por qué se eligió esta alternativa:</strong></p>
            <p>{description}</p>
    """

    for key, value in arguments.items():
        # Extraemos el número del criterio para buscar su nombre en criteria_names
        criterion_number = key.replace("argumentacion", "")
        criterion_name = criteria_names.get(f"criteria{criterion_number}", f"Criterio {criterion_number}")
        html_text += f"""
            <p><strong>{criterion_name}:</strong> {value}</p>
        """

    html_text += """
            <a href="/alternativa-principal" target="_blank" class="button">Elegir como Principal</a>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_text)


@app.get("/alternativa-principal", response_class=HTMLResponse)
async def alternativa_principal():

    db = SessionLocal()
    alternativas = crud.obtener_ulima_alternativa(db)
    print(alternativas.elegida)
    crud.elegir_alternativa(db, alternativas.id_alternativa)

    html_text = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alternativa Principal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }
            .container {
                max-width: 600px;
                margin: auto;
                padding: 20px;
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Alternativa Principal</h1>
            <p>La alternativa ha sido elegida como principal.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_text)