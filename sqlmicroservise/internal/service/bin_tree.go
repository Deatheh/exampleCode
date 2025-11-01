package service

import "notifications/internal/database/postgres"

type BinTreeService struct {
	repository *postgres.BinTreeTable
}

func (es BinTreeService) Add(kStr, vStr string) (int, error) {
	id, err := es.repository.Add(kStr, vStr)
	if err != nil {
		return 0, err
	}
	return id, nil
}
