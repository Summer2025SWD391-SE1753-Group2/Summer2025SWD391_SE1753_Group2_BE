from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.role import RoleCreate, RoleOut
from app.services.role_service import create_role, get_role_by_id, get_all_roles
from app.core.deps import get_db

# Initialize the API router for role-related operations.
# Tags help categorize endpoints in the OpenAPI (Swagger UI) documentation.
router = APIRouter(tags=["Roles"])


@router.post("/", response_model=RoleOut, status_code=201)
def create_new_role(
    role: RoleCreate,
    db: Session = Depends(get_db)
) -> RoleOut:
    """
    **Create a new role.**

    This endpoint allows the creation of a new role in the system.
    It expects a RoleCreate schema containing the role details.

    - **Parameters**:
        - `role`: The Pydantic model for creating a new role.
        - `db`: Database session dependency.

    - **Returns**:
        - The newly created `RoleOut` object.
    """
    return create_role(db, role)


@router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: int,
    db: Session = Depends(get_db)
) -> RoleOut:
    """
    **Retrieve a single role by its ID.**

    This endpoint fetches the details of a specific role using its unique identifier.

    - **Parameters**:
        - `role_id`: The integer ID of the role to retrieve.
        - `db`: Database session dependency.

    - **Returns**:
        - The `RoleOut` object corresponding to the given ID.
    """
    # The import for get_role_by_id is moved to the top-level imports for PEP 8 consistency.
    return get_role_by_id(db, role_id)


@router.get("/", response_model=List[RoleOut])
def list_roles(
    db: Session = Depends(get_db)
) -> List[RoleOut]:
    """
    **List all available roles.**

    This endpoint retrieves a list of all roles stored in the database.

    - **Parameters**:
        - `db`: Database session dependency.

    - **Returns**:
        - A list of `RoleOut` objects representing all roles.
    """
    # The import for get_all_roles is moved to the top-level imports for PEP 8 consistency.
    return get_all_roles(db)

