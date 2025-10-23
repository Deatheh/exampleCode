package main

import (
	"log"
	"notifications/internal/api/handler"
	"notifications/internal/api/server"
	"notifications/internal/config"
	"notifications/internal/database"
	"notifications/internal/database/postgres"
	"notifications/internal/service"

	"github.com/joho/godotenv"
)

// @title IQJ NOTIFICATIONS MICROSERVICE
// @version 1.0
// @BasePath /
func main() {
	if err := godotenv.Load(".env"); err != nil {
		log.Println("No .env file found")
	}

	envConf := config.NewEnvConfig()
	config.PrintConfigWithHiddenSecrets(envConf)

	repositorySQL := postgres.NewDatabaseInstance(envConf)
	repository := &database.Repository{DatabaseRepository: repositorySQL}
	services := service.NewService(repository, envConf)
	handlers := handler.NewHandler(services, envConf)

	apiServer := server.APIServer{Port: "3000", EnvConf: envConf, Handler: handlers}
	apiServer.Run()
}
