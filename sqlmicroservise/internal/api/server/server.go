package server

import (
	"fmt"
	"log"
	"notifications/internal/api/handler"
	"notifications/internal/config"
	"os"
)

type APIServer struct {
	Port    string
	EnvConf *config.Config
	Handler *handler.Handler
}

func (s *APIServer) Run() {
	if s.EnvConf.Application.ProductionType == "prod" {
		os.Setenv("ENV", "production")
		if err := s.Handler.InitRoutes().Listen(fmt.Sprintf(":%v", s.Port)); err != nil {
			log.Fatal(fmt.Errorf("server run error: %w", err))
		}
	}

	if err := s.Handler.InitRoutes().Listen(fmt.Sprintf(":%v", s.Port)); err != nil {
		log.Fatal(fmt.Errorf("server run error: %w", err))
	}
}
