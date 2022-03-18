from typing import Any, Dict, List, Optional, Union

import great_expectations.exceptions as ge_exceptions
from great_expectations.core.profiler_types_mapping import ProfilerTypeMapping
from great_expectations.rule_based_profiler.types import (
    InferredSemanticDomainType,
    SemanticDomainTypes,
)
from great_expectations.rule_based_profiler.types.semantic_type_filter import (
    SemanticTypeFilter,
)


class SimpleSemanticTypeFilter(SemanticTypeFilter):
    """
    This class provides default implementation methods, any of which can be overwritten with different mechanisms.
    """

    def parse_semantic_domain_type_argument(
        self,
        semantic_types: Optional[
            Union[str, SemanticDomainTypes, List[Union[str, SemanticDomainTypes]]]
        ] = None,
    ) -> List[SemanticDomainTypes]:
        if semantic_types is None:
            return []

        semantic_type: Union[str, SemanticDomainTypes]
        if isinstance(semantic_types, str):
            semantic_types = semantic_types.upper()
            return [
                SemanticDomainTypes[semantic_type] for semantic_type in [semantic_types]
            ]
        if isinstance(semantic_types, SemanticDomainTypes):
            return [semantic_type for semantic_type in [semantic_types]]
        elif isinstance(semantic_types, list):
            if all(
                [isinstance(semantic_type, str) for semantic_type in semantic_types]
            ):
                semantic_types = [
                    semantic_type.upper() for semantic_type in semantic_types
                ]
                return [
                    SemanticDomainTypes[semantic_type]
                    for semantic_type in semantic_types
                ]
            elif all(
                [
                    isinstance(semantic_type, SemanticDomainTypes)
                    for semantic_type in semantic_types
                ]
            ):
                return [semantic_type for semantic_type in semantic_types]
            else:
                raise ValueError(
                    "All elements in semantic_types list must be either of str or SemanticDomainTypes type."
                )
        else:
            raise ValueError("Unrecognized semantic_types directive.")

    def infer_semantic_domain_type_from_table_column_type(
        self,
        column_types_dict_list: List[Dict[str, Any]],
        column_name: str,
    ) -> InferredSemanticDomainType:
        # Note: As of Python 3.8, specifying argument type in Lambda functions is not supported by Lambda syntax.
        column_types_dict_list = list(
            filter(
                lambda column_type_dict: column_name == column_type_dict["name"],
                column_types_dict_list,
            )
        )
        if len(column_types_dict_list) != 1:
            raise ge_exceptions.ProfilerExecutionError(
                message=f"""Error: {len(column_types_dict_list)} columns were found while obtaining semantic type \
    information.  Please ensure that the specified column name refers to exactly one column.
    """
            )

        column_type: str = str(column_types_dict_list[0]["type"]).upper()

        semantic_column_type: SemanticDomainTypes
        if column_type in (
            {type_name.upper() for type_name in ProfilerTypeMapping.INT_TYPE_NAMES}
            | {type_name.upper() for type_name in ProfilerTypeMapping.FLOAT_TYPE_NAMES}
        ):
            semantic_column_type = SemanticDomainTypes.NUMERIC
        elif column_type in {
            type_name.upper() for type_name in ProfilerTypeMapping.STRING_TYPE_NAMES
        }:
            semantic_column_type = SemanticDomainTypes.TEXT
        elif column_type in {
            type_name.upper() for type_name in ProfilerTypeMapping.BOOLEAN_TYPE_NAMES
        }:
            semantic_column_type = SemanticDomainTypes.LOGIC
        elif column_type in {
            type_name.upper() for type_name in ProfilerTypeMapping.DATETIME_TYPE_NAMES
        }:
            semantic_column_type = SemanticDomainTypes.DATETIME
        elif column_type in {
            type_name.upper() for type_name in ProfilerTypeMapping.BINARY_TYPE_NAMES
        }:
            semantic_column_type = SemanticDomainTypes.BINARY
        elif column_type in {
            type_name.upper() for type_name in ProfilerTypeMapping.CURRENCY_TYPE_NAMES
        }:
            semantic_column_type = SemanticDomainTypes.CURRENCY
        elif column_type in {
            type_name.upper() for type_name in ProfilerTypeMapping.IDENTIFIER_TYPE_NAMES
        }:
            semantic_column_type = SemanticDomainTypes.IDENTIFIER
        elif column_type in (
            {
                type_name.upper()
                for type_name in ProfilerTypeMapping.MISCELLANEOUS_TYPE_NAMES
            }
            | {type_name.upper() for type_name in ProfilerTypeMapping.RECORD_TYPE_NAMES}
        ):
            semantic_column_type = SemanticDomainTypes.MISCELLANEOUS
        else:
            semantic_column_type = SemanticDomainTypes.UNKNOWN

        inferred_semantic_column_type: InferredSemanticDomainType = (
            InferredSemanticDomainType(
                semantic_domain_type=semantic_column_type,
                details={
                    "algorithm_type": "deterministic",
                    "mechanism": "lookup_table",
                    "source": "great_expectations.profile.base.ProfilerTypeMapping",
                },
            )
        )

        return inferred_semantic_column_type