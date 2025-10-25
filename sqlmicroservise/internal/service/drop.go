package service

import "notifications/internal/database/postgres"

type DropService struct {
	repository *postgres.DropTable
}

func (ds DropService) Drop() error {
	err := ds.repository.Drop()
	if err != nil {
		return err
	}
	return nil
}
