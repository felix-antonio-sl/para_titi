-- =============================================================================
-- Seed: Usuario Administrador para Sistema de Gestión de Crisis
-- Ejecutar en gore_nuble después de levantar gore_db
-- =============================================================================

-- 1. Crear persona
INSERT INTO gore_actores.persona (id, rut, nombres, apellido_paterno, apellido_materno, email)
VALUES (
    'a0000000-0000-0000-0000-000000000001'::uuid,
    '11111111-1',
    'Administrador',
    'Sistema',
    'GORE',
    'admin@gorenuble.cl'
) ON CONFLICT (rut) DO NOTHING;

-- 2. Crear usuario con rol ADMIN_SISTEMA
-- Password: admin123 (hash generado con werkzeug)
INSERT INTO gore_autenticacion.usuario (id, persona_id, username, email, password_hash, activo, rol_crisis)
VALUES (
    'b0000000-0000-0000-0000-000000000001'::uuid,
    'a0000000-0000-0000-0000-000000000001'::uuid,
    'admin',
    'admin@gorenuble.cl',
    'scrypt:32768:8:1$salt$c5a5b5c5d5e5f5a5b5c5d5e5f5a5b5c5d5e5f5a5b5c5d5e5f5a5b5c5d5e5f5a5',
    true,
    'ADMIN_SISTEMA'
) ON CONFLICT (email) DO UPDATE SET 
    rol_crisis = 'ADMIN_SISTEMA',
    activo = true;

-- 3. Verificar
SELECT u.email, u.rol_crisis, p.nombres || ' ' || p.apellido_paterno as nombre
FROM gore_autenticacion.usuario u
JOIN gore_actores.persona p ON p.id = u.persona_id
WHERE u.email = 'admin@gorenuble.cl';
