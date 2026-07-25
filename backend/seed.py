import sys
import uuid
from app import create_app
from app.core.extensions import db
from app.models.role import Role, Permission, RolePermission
from app.models.user import User
from app.core.security import hash_password

app = create_app()

def seed_database():
    with app.app_context():
        print("Ensuring tables are created...")
        db.create_all()

        # 1. Create or get Admin Role
        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            admin_role = Role(id=str(uuid.uuid4()), name="Admin", description="System Administrator with full permissions")
            db.session.add(admin_role)
            print("Created Admin role.")
        else:
            print("Admin role already exists.")

        # 2. Create or get permissions
        permissions_list = [
            ("manage_users", "Manage users and roles"),
            ("manage_clients", "Manage clients"),
            ("manage_integrations", "Manage integrations"),
            ("execute_integrations", "Execute integration workflows"),
            ("view_dashboard", "View monitoring dashboard"),
            ("use_copilot", "Use AI copilot")
        ]

        created_perms = []
        for name, desc in permissions_list:
            perm = Permission.query.filter_by(name=name).first()
            if not perm:
                perm = Permission(id=str(uuid.uuid4()), name=name, description=desc)
                db.session.add(perm)
                print(f"Created permission: {name}")
            created_perms.append(perm)

        db.session.commit()

        # Assign permissions to Admin role
        for perm in created_perms:
            rp = RolePermission.query.filter_by(role_id=admin_role.id, permission_id=perm.id).first()
            if not rp:
                rp = RolePermission(role_id=admin_role.id, permission_id=perm.id)
                db.session.add(rp)
        db.session.commit()

        # 3. Create Default Admin User
        admin_user = User.query.filter_by(email="admin@syncbridge.ai").first()
        if not admin_user:
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@syncbridge.ai",
                password_hash=hash_password("Admin123!"),
                first_name="System",
                last_name="Administrator",
                role_id=admin_role.id,
                is_active=True,
                is_locked=False
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin user: admin@syncbridge.ai / Admin123!")
        else:
            print("Default admin user admin@syncbridge.ai already exists.")

if __name__ == "__main__":
    seed_database()
