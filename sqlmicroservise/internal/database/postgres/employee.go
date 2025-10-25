package postgres

import (
	"database/sql"
	"fmt"
)

type EmployeeTable struct {
	db *sql.DB // Указатель на подключение к базе данных
}

func (et *EmployeeTable) Add(columns, values string) (int, error) {
	insertQuery := fmt.Sprintf(`
	INSERT INTO employee (%s)
		VALUES (%s)
		RETURNING id
	`, columns, values)
	var id int
	err := et.db.QueryRow(insertQuery).Scan(&id)

	if err != nil {
		return 0, fmt.Errorf("Employee.Add: %v", err)
	}

	return id, nil
}

func (et *EmployeeTable) GetAll() ([]map[string]interface{}, error) {
	query := `
	SELECT * FROM employee
	`
	rows, err := et.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get data from employee table: %v", err)
	}

	defer rows.Close()

	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	var results []map[string]interface{}

	for rows.Next() {
		values := make([]interface{}, len(columns))
		scanArgs := make([]interface{}, len(columns))

		for i := range values {
			scanArgs[i] = &values[i]
		}

		err := rows.Scan(scanArgs...)
		if err != nil {
			return nil, err
		}

		rowMap := make(map[string]interface{})
		for i, col := range columns {
			switch v := values[i].(type) {
			case []byte:
				rowMap[col] = string(v)
			default:
				rowMap[col] = v
			}
		}

		results = append(results, rowMap)
	}

	return results, nil
}

func (et *EmployeeTable) GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error) {
	query := fmt.Sprintf(`
	SELECT %s FROM employee 
		`, outputCol)
	query += joinStrings
	query += whereStrings
	query += groupByStrings
	query += havingStrings
	query += orderByStrings

	rows, err := et.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get data from employee table: %v", err)
	}

	defer rows.Close()

	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	var results []map[string]interface{}

	for rows.Next() {
		values := make([]interface{}, len(columns))
		scanArgs := make([]interface{}, len(columns))

		for i := range values {
			scanArgs[i] = &values[i]
		}

		err := rows.Scan(scanArgs...)
		if err != nil {
			return nil, err
		}

		rowMap := make(map[string]interface{})
		for i, col := range columns {
			switch v := values[i].(type) {
			case []byte:
				rowMap[col] = string(v)
			default:
				rowMap[col] = v
			}
		}

		results = append(results, rowMap)
	}

	return results, nil
}

func (et *EmployeeTable) AlterTable(alterStrings string) error {
	query := `
	ALTER TABLE employee
	`
	query += alterStrings

	et.db.QueryRow(query)

	return nil
}

func (et *EmployeeTable) GetAllColumns() ([][]string, error) {
	query := `
	SELECT 
		c.column_name, 
		c.is_nullable,
		CASE 
			WHEN c.data_type = 'USER-DEFINED' THEN pgt.typname
			ELSE c.data_type 
		END as data_type
	FROM information_schema.columns c
	LEFT JOIN pg_attribute pa ON c.table_name = pa.attrelid::regclass::text 
		AND c.column_name = pa.attname
	LEFT JOIN pg_type pgt ON pa.atttypid = pgt.oid
	WHERE c.table_name = 'employee';
	`
	rows, err := et.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get columns employee table: %v", err)
	}
	defer rows.Close()

	var columns [][]string

	for rows.Next() {
		var col []string
		var c, n, t string
		err := rows.Scan(&c, &n, &t)
		col = append(col, c)
		col = append(col, n)
		col = append(col, t)
		if err != nil {
			return nil, fmt.Errorf("News.getAllColumns: %v", err)
		}
		columns = append(columns, col)
	}

	return columns, nil
}

func (et *EmployeeTable) GetAllConstraints() ([]string, error) {
	query := `
	SELECT constraint_name
		FROM information_schema.table_constraints
		WHERE table_name = 'employee'
		ORDER BY constraint_name;
	`
	rows, err := et.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get columns employee table: %v", err)
	}
	defer rows.Close()

	var columns []string

	for rows.Next() {
		var c string
		err := rows.Scan(&c)
		if err != nil {
			return nil, fmt.Errorf("News.getAllConstaints: %v", err)
		}
		columns = append(columns, c)
	}

	return columns, nil
}

func newEmployeeTable(db *sql.DB, query string) (*EmployeeTable, error) {
	_, err := db.Exec(query)
	if err != nil {
		return nil, fmt.Errorf("failed to create employee table: %v", err)
	}
	return &EmployeeTable{db: db}, nil
}
