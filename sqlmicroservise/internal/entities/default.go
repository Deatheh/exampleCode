package entities

type ErrorResponse struct {
	Error string `json:"error"`
}

type Id struct {
	Id int `json:"id"`
}

type Message struct {
	Message string `json:"message"`
}

type InputAlter struct {
	AlterStrings string `json:"alter_string"`
}
