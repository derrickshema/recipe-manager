from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, status

from ..utilities.rbac import require_edit_menu_access, require_read_restaurant_access

from ..models.user import User

from ..db.session import get_session
from ..models.recipe import Recipe, RecipeCreate, RecipeRead, RecipeUpdate
router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    restaurant_id: int,
    recipe: RecipeCreate, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_edit_menu_access())
):
    """
    Creates a new recipe in the database for a specific restaurant.
    The restaurant_id is taken from the query parameter to ensure proper access control.
    """
    # restaurant_id from query param will be validated by require_edit_menu_access
    new_recipe = Recipe(
        **recipe.model_dump(),
        restaurant_id=restaurant_id
    )
    session.add(new_recipe)
    session.commit()
    session.refresh(new_recipe)
    return new_recipe

@router.get("/", response_model=list[RecipeRead])
async def get_recipes(
    restaurant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_read_restaurant_access())
):
    """
    Fetches all recipes for a specific restaurant.
    The restaurant_id query parameter is used for both access control and filtering.
    """
    # Access control is handled by require_read_restaurant_access()
    # which checks if the user has permission to access this restaurant
    recipes = session.exec(
        select(Recipe).where(Recipe.restaurant_id == restaurant_id)
    ).all()
    return recipes

@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(
    recipe_id: int,
    restaurant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_read_restaurant_access())
):
    """
    Fetches a recipe by ID from the database.
    The restaurant_id query parameter is used for access control and validation.
    """
    recipe = session.exec(
        select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.restaurant_id == restaurant_id
        )
    ).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or you don't have access to it"
        )
    return recipe

@router.put("/{recipe_id}", response_model=Recipe)
async def update_recipe(recipe_id: int, updated_recipe: RecipeUpdate, session: Session = Depends(get_session), current_user: User = Depends(require_edit_menu_access())):
    """
    Updates a recipe's information in the database.
    """
    existing_recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if not existing_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    for key, value in updated_recipe.model_dump(exclude_unset=True).items():
        setattr(existing_recipe, key, value)

    session.add(existing_recipe)
    session.commit()
    session.refresh(existing_recipe)
    return existing_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int, session: Session = Depends(get_session), current_user: User = Depends(require_edit_menu_access())):
    """
    Deletes a recipe by ID from the database.
    """
    recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    session.delete(recipe)
    session.commit()
    return {"detail": "Recipe deleted successfully"}