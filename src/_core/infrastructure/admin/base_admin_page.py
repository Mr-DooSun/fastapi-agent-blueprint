from dataclasses import dataclass, field


@dataclass
class ColumnConfig:
    """Column configuration for admin CRUD table."""

    field_name: str
    header_name: str
    sortable: bool = True
    searchable: bool = False
    hidden: bool = False
    masked: bool = False
    width: int | None = None


@dataclass
class BaseAdminPage:
    """Base configuration for auto-generated admin CRUD pages.

    Each domain creates an instance with its column config.
    The rendering logic lives in _core renderers module.
    """

    domain_name: str
    display_name: str
    icon: str = "list"
    columns: list[ColumnConfig] = field(default_factory=list)
    searchable_fields: list[str] = field(default_factory=list)
    sortable_fields: list[str] = field(default_factory=list)
    default_sort_field: str = "id"
    default_sort_order: str = "desc"
    page_size: int = 20
    readonly: bool = True

    def get_visible_columns(self) -> list[ColumnConfig]:
        return [c for c in self.columns if not c.hidden]

    def get_masked_field_names(self) -> set[str]:
        return {c.field_name for c in self.columns if c.masked}
