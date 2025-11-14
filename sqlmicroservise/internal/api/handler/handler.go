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
		employee.Get("/constrains", h.HandlerConstrainsEmployee)
	}
	project := r.Group("/project")
	{
		project.Post("", h.HandlerAddProject)
		project.Get("", h.HandlerGetAllProject)
		project.Get("/filters", h.HandlerGetAllProjectByFilters)
		project.Post("/alter", h.HandlerAlterTableProject)
		project.Get("/columns", h.HandlerColumnsProject)
		project.Get("/constrains", h.HandlerConstrainsProject)
	}
	task := r.Group("/task")
	{
		task.Post("", h.HandlerAddTask)
		task.Get("", h.HandlerGetAllTask)
		task.Get("/filters", h.HandlerGetAllTaskByFilters)
		task.Post("/alter", h.HandlerAlterTableTask)
		task.Get("/columns", h.HandlerColumnsTask)
		task.Get("/constrains", h.HandlerContsraintsTask)
	}
	drop := r.Group("/drop")
	{
		drop.Delete("", h.HandlerDrop)
	}
	userType := r.Group("/user_type")
	{
		userType.Get("", h.HandlerGetAllUserType)
		userType.Post("", h.HandlerAddType)
		userType.Get("/values", h.HandlerGetAllUserTypeWithValues)
	}
	return r
}

func (h *Handler) Hello(c fiber.Ctx) error {
	return c.SendString("Добро пожаловать!")
}
