from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.membership import OrgRole
from ..utilities.users_utils import require_org_roles

from ..models.user import User
from .auth_routes import get_current_user

from ..db.session import get_session
from ..models.recipe import Recipe, RecipeCreate, RecipeRead, RecipeUpdate
router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_student(student: RecipeCreate, session: Session = Depends(get_session), current_user: User = Depends(require_org_roles(OrgRole.EMPLOYEE))):
    """
    Creates a new recipe in the database.
    """
    new_recipe = Recipe.model_validate(student)
    session.add(new_recipe)
    session.commit()
    session.refresh(new_recipe)
    return new_recipe

@router.get("/", response_model=list[RecipeRead])
async def get_students(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """
    Fetches all recipes from the database.
    """
    recipes = session.exec(select(RecipeRead)).all()
    return recipes

@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_student(recipe_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """
    Fetches a recipe by ID from the database.
    """
    recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe

@router.put("/{recipe_id}", response_model=Recipe)
async def update_student(recipe_id: int, updated_student: RecipeUpdate, session: Session = Depends(get_session), current_user: User = Depends(require_org_roles(OrgRole.EMPLOYEE))):
    """
    Updates a recipe's information in the database.
    """
    existing_recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if not existing_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    for key, value in updated_student.model_dump(exclude_unset=True).items():
        setattr(existing_recipe, key, value)

    session.add(existing_recipe)
    session.commit()
    session.refresh(existing_recipe)
    return existing_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(recipe_id: int, session: Session = Depends(get_session), current_user: User = Depends(require_org_roles(OrgRole.EMPLOYEE))):
    """
    Deletes a student by ID from the database.
    """
    recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    session.delete(recipe)
    session.commit()
    return {"detail": "Recipe deleted successfully"}