# ---------------------------------------------------------------------------- +
# test_budget_model.py
# ---------------------------------------------------------------------------- +
#region imports
# python standard libraries
import pytest, os
from pathlib import Path
from typing import Type, Any
# third-party libraries
import inspect
import logging, p3_utils as p3u, p3logging as p3l
# local libraries
from budman_namespace import *
from budget_domain_model import BDMBaseInterface
from budget_domain_model import BudgetDomainModel
#endregion imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
model_class_name = "BudgetDomainModel"
model_class: Type[Any] = object()
#endregion Globals
# ---------------------------------------------------------------------------- +
class TestBudgetDomainModelBinding:
    """Test the Dynamic Class Binding class."""

    @pytest.fixture()
    def model_class(self) -> Type[object]:
        """Fixture to provide the BudgetDomainModel class."""
        global model_class, model_class_name
        cls = globals()[model_class_name]
        if not inspect.isclass(cls):
            raise TypeError(f"{model_class_name} is not a class")
        if not issubclass(cls, BDMBaseInterface):
            raise TypeError(f"{model_class_name} is not a subclass of BDMBaseInterface")
        model_cls = cls
        return model_cls
    # ------------------------------------------------------------------------ +    
    def test_budget_domain_model_binding(self, model_class) -> None:
        """Test the Dynamic Class Binding class."""
        try:
            logger.info(self.test_budget_domain_model_binding.__doc__)
            # Create a BudgetDomainModel instance.
            bdm = model_class()
            assert isinstance(bdm, BDMBaseInterface), \
                "BudgetDomainModel should be a BudgetDomainModel instance"
            assert isinstance(bdm, BudgetDomainModel), \
                "BudgetDomainModel should be a BudgetDomainModel instance"
            assert bdm.uid is not None, \
                "BudgetDomainModel uid should not be None"
            assert isinstance(bdm.uid, str), \
                "BudgetDomainModel uid should be a string"
            assert bdm.name is not None, \
                "BudgetDomainModel name should not be None"
            assert isinstance(bdm.name, str), \
                "BudgetDomainModel name should be a string"
            bdm_store_path = bdm.bdm_store_abs_path()
            assert bdm_store_path is not None, \
                "BudgetDomainModel store path should not be None"
            assert isinstance(bdm_store_path, Path), \
                "BudgetDomainModel store path should be a Path object"
            # Brand new bdm should not resolve yet.
            with pytest.raises(Exception) as excinfo:
                bdm.bdm_stor()

        except Exception as e:
            pytest.fail(f"BudgetDomainModel raised an exception: {str(e)}")