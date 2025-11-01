package postgres

import (
	"database/sql"
	"fmt"
)

type BinTreeTable struct {
	db *sql.DB // Указатель на подключение к базе данных
}

func (pt *BinTreeTable) Add(columns, values string) (int, error) {
	insertQuery := fmt.Sprintf(`
	INSERT INTO binary_tree (%s)
		VALUES (%s)
		RETURNING id
	`, columns, values)
	var id int
	err := pt.db.QueryRow(insertQuery).Scan(&id)

	if err != nil {
		return 0, fmt.Errorf("Project.Add: %v", err)
	}

	return id, nil
}

func newBinTreeTable(db *sql.DB, query string) (*BinTreeTable, error) {
	_, err := db.Exec(query)
	if err != nil {
		return nil, fmt.Errorf("failed to create project table: %v", err)
	}
	return &BinTreeTable{db: db}, nil

}
