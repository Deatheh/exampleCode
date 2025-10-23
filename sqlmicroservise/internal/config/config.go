package config

import (
	"fmt"
	"os"
	"strings"
)

type Application struct {
	ProductionType        string
	CryptographySecretKey string
	LogPath               string
}

type Email struct {
	ValidDomain            []string
	Blacklist              []string
	MondayOfFirstStudyWeek string
}

type Db struct {
	Host     string
	Port     string
	User     string
	Password string
	Database string
}

type Config struct {
	Application Application
	Db          Db
}

func NewEnvConfig() *Config {
	return &Config{
		Application: Application{
			ProductionType:        os.Getenv("PRODUCTION_TYPE"),
			CryptographySecretKey: os.Getenv("CRYPTOGRAPHY_SECRET_KEY"),
		},
		Db: Db{
			Host:     os.Getenv("POSTGRES_HOST"),
			Port:     os.Getenv("POSTGRES_PORT"),
			User:     os.Getenv("POSTGRES_USER"),
			Password: os.Getenv("POSTGRES_PASSWORD"),
			Database: os.Getenv("POSTGRES_DB"),
		},
	}
}

func PrintConfigWithHiddenSecrets(config *Config) {
	// Функция для маскировки секретов
	mask := func(s string) string {
		if s == "" {
			return ""
		}
		return strings.Repeat("*", len(s))
	}

	fmt.Println("=== Application Config ===")
	fmt.Printf("ProductionType: %s\n", config.Application.ProductionType)
	fmt.Printf("CryptographySecretKey: %s\n", mask(config.Application.CryptographySecretKey))

	fmt.Println("\n=== Database Config ===")
	fmt.Printf("Host: %s\n", config.Db.Host)
	fmt.Printf("Port: %s\n", config.Db.Port)
	fmt.Printf("User: %s\n", config.Db.User)
	fmt.Printf("Password: %s\n", mask(config.Db.Password))
	fmt.Printf("Database: %s\n", config.Db.Database)

}
