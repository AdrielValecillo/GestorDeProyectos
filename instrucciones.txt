1. Crear un entorno virtual con Python  
   py -m venv env

2. Activar el entorno virtual  
   .\env\Scripts\activate

3. Instalar las dependencias del proyecto  
   pip install -r requirements.txt

4. Configurar las variables de entorno  
   - Crea un archivo llamado .env en el directorio raíz del proyecto.  
   - Copia el contenido del archivo env.txt dentro del archivo .env.  
   - Ajusta los valores de las variables de entorno según las necesidades del proyecto.

5. Iniciar el proyecto  
   uvicorn main:app --reload

6. Abrir la aplicación en el navegador  
   http://localhost:8000/
