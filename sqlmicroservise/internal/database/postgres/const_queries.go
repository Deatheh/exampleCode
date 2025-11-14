package postgres

//Создание Таблиц при первом заходе

const (
	createTableEmployee = `
		DO $$ 
		BEGIN 
			IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'duty') THEN
				CREATE TYPE DUTY AS ENUM ('Frontend', 'Backend', 'Devops', 'Teamlead', 'HR', 'PM', 'CEO');
			END IF;
		END $$;
		CREATE TABLE IF NOT EXISTS employee (
			id SERIAL PRIMARY KEY,
			full_name VARCHAR(300) NOT NULL,
			age INTEGER NOT NULL CHECK (age > 18 AND age < 120),
			salary INTEGER NOT NULL CHECK (salary > 80000),
			duty DUTY NOT NULL,
			skills VARCHAR(300)[]
		);`

	createTableProject = `
		CREATE TABLE IF NOT EXISTS project (
			id SERIAL PRIMARY KEY,
			name VARCHAR(300) NOT NULL,
			deadline DATE,
			prize INTEGER CHECK (prize >= 0),
			customer VARCHAR(500),
			finished BOOLEAN NOT NULL
		);
	`

	createTableTask = `
		DO $$ 
		BEGIN 
			IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status') THEN
				CREATE TYPE STATUS AS ENUM ('Новая', 'В работе', 'Можно проверять', 'Завершена');
			END IF;
		END $$;
		CREATE TABLE IF NOT EXISTS task (
			id SERIAL PRIMARY KEY,
			employee_id INTEGER NOT NULL REFERENCES employee(id),
			project_id INTEGER NOT NULL REFERENCES project(id),
			name VARCHAR(300) NOT NULL,
			description TEXT,
			deadline DATE,
			status STATUS
		);
	`
)
