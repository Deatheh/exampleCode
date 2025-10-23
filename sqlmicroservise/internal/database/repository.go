package database

import "notifications/internal/database/postgres"

type Repository struct {
	DatabaseRepository *postgres.DatabaseRepository
}
