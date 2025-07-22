#!/bin/bash
# filepath: g:\Meu Drive\Cursos e Treinamentos\Cientista de Dados\Treinamento Python\I2A2\Desafios\Desafio 2 - Projeto - 11062025\agente_nfs\Scripts\entrypoint.sh
echo "GOOGLE_API_KEY=\"AIzaSyAOhPIBGBJyhmQFGwcuMxGqS0MniA_7TQ8\"" > /app/.env
exec "$@"