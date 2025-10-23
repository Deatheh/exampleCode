package handler

import (
	"notifications/internal/config"
	"notifications/internal/service"

	_ "notifications/docs"

	"github.com/Flussen/swagger-fiber-v3"
	"github.com/gofiber/fiber/v3"
)

const (
	DefaultRoute = "/"
)

type Handler struct {
	services *service.Service
	envConf  *config.Config
}

func NewHandler(services *service.Service, envConf *config.Config) *Handler {
	return &Handler{services: services, envConf: envConf}
}

// Функция для создания роутера, добавления к нему CORSMiddleware
// и объявления путей для всех запросов.
func (h *Handler) InitRoutes() *fiber.App {
	r := fiber.New()
	r.Get("/swagger/*", swagger.HandlerDefault)
	r.Get(DefaultRoute, h.Hello)
	employee := r.Group("/employee")
	{
		employee.Post("", h.HandlerAddEmployee)
		employee.Get("", h.HandlerGetAllEmployee)
		employee.Get("/filters", h.HandlerGetAllEmployeeByFilters)
		employee.Post("/alter", h.HandlerAlterTableEmployee)
		employee.Get("/columns", h.HandlerColumnsEmployee)
	}
	project := r.Group("/project")
	{
		project.Post("", h.HandlerAddProject)
		project.Get("", h.HandlerGetAllProject)
		project.Get("/filters", h.HandlerGetAllProjectByFilters)
		project.Post("/alter", h.HandlerAlterTableProject)
		project.Get("/columns", h.HandlerColumnsProject)
	}
	task := r.Group("/task")
	{
		task.Post("", h.HandlerAddTask)
		task.Get("", h.HandlerGetAllTask)
		task.Get("/filters", h.HandlerGetAllTaskByFilters)
		task.Post("/alter", h.HandlerAlterTableTask)
		task.Get("/columns", h.HandlerColumnsTask)
	}
	return r
}

func (h *Handler) Hello(c fiber.Ctx) error {
	return c.SendString("Добро пожаловать!")
}
