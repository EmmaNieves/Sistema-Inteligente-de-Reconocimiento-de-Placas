import { Switch, Route, Redirect } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/hooks/use-auth";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Estadisticas from "@/pages/Estadisticas";
import Detecciones from "@/pages/Detecciones";
import Alertas from "@/pages/Alertas";
import Vehiculos from "@/pages/Vehiculos";
import Camaras from "@/pages/Camaras";
import Usuarios from "@/pages/Usuarios";
import NotFound from "@/pages/not-found";
import Audiencias from "@/pages/Audiencias";
import Mapa from "@/pages/Mapa";

function Router() {
  return (
    <Switch>
      <Route path="/login" component={Login} />
      
      {/* VISUALIZADORES - Solo lectura */}
      <Route path="/dashboard">
        <ProtectedRoute requiredRole="visualizador"><Dashboard /></ProtectedRoute>
      </Route>
      <Route path="/estadisticas">
        <ProtectedRoute requiredRole="visualizador"><Estadisticas /></ProtectedRoute>
      </Route>
      <Route path="/audiencias">
        <ProtectedRoute requiredRole="visualizador"><Audiencias /></ProtectedRoute>
      </Route>
      <Route path="/detecciones">
        <ProtectedRoute requiredRole="visualizador"><Detecciones /></ProtectedRoute>
      </Route>
      <Route path="/alertas">
        <ProtectedRoute requiredRole="visualizador"><Alertas /></ProtectedRoute>
      </Route>
      <Route path="/mapa">
        <ProtectedRoute requiredRole="visualizador"><Mapa /></ProtectedRoute>
      </Route>

      {/* OPERADORES - Lectura + Escritura */}
      <Route path="/vehiculos">
        <ProtectedRoute requiredRole="operador"><Vehiculos /></ProtectedRoute>
      </Route>
      <Route path="/camaras">
        <ProtectedRoute requiredRole="operador"><Camaras /></ProtectedRoute>
      </Route>

      {/* ADMINISTRADORES - Acceso total */}
      <Route path="/usuarios">
        <ProtectedRoute requiredRole="administrador"><Usuarios /></ProtectedRoute>
      </Route>

      <Route path="/">
        <Redirect to="/login" />
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
