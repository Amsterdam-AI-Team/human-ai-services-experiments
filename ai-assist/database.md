# Database Setup 

Deze handleiding beschrijft hoe je een PostgreSQL-database kunt opzetten en starten met behulp van Docker. 

## Vereisten 

 - Docker moet geïnstalleerd zijn op je systeem.  
 - Basiskennis van de terminal.

## 1. Bouw de Docker-image 

Zorg ervoor dat je in de map bent waar de Dockerfile zich bevindt. Voer het volgende commando uit om de Docker-image te bouwen: 

    docker build -t mijn-postgres:latest . 

mijn-postgres is de naam van de image. latest is de tag (optioneel, maar aanbevolen). 

## 2. Start de database-container 

Start een nieuwe container met de volgende opdracht: 

    docker run -d --name mijn-postgres-container -p 5432:5432 mijn-postgres:latest 

-d: Start de container in de achtergrond. 
--name mijn-postgres-container: Geeft de container een herkenbare naam. 
-p 5432:5432: Verbindt poort 5432 van de container met poort 5432 op je hostmachine. 

## 3. Verbind met de database 

Verbindingsgegevens: 
Host: 
localhost Port: 5432 
Database: aifutures 
Gebruiker: aifutures 
Wachtwoord: aifutures 

Voorbeeld met psql: 

	psql -h localhost -p 5432 -U aifutures -d aifutures 

 Je wordt gevraagd om het wachtwoord. Voer aifutures in. 

## 4. Stoppen en verwijderen van de container 

Stop de container: docker stop mijn-postgres-container Verwijder de container: docker rm mijn-postgres-container 

## 5. Veelvoorkomende problemen 

### Image niet zichtbaar na build 

Controleer of je de image een naam hebt gegeven tijdens het bouwen: 

    docker build -t mijn-postgres:latest . 

### Poort 5432 is al in gebruik 

Controleer welke processen de poort gebruiken: 

    lsof -i :5432

Stop het proces of gebruik een andere poort: 

    docker run -d --name mijn-postgres-container -p 5433:5432 mijn-postgres:latest

Met deze stappen kun je eenvoudig een PostgreSQL-database opzetten en gebruiken met Docker.
