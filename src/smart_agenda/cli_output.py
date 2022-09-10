"""Anything related to how the cli generates its output."""

from datetime import timedelta

from rich.table import Table

from smart_agenda.lib import Agenda, format_td


def _get_empty_table(title=None) -> Table:
    table = Table(show_header=False)
    table.add_column("Item")
    table.add_column("Plan", justify="right", no_wrap=True)
    table.add_column("Delta", justify="right", no_wrap=True, min_width=6)
    if title:
        table.title = title
    return table


def render_initial_agenda(agenda: Agenda) -> Table:
    """Render table for an agenda that hasn't been started yet."""
    table = _get_empty_table(agenda.title)
    for item in agenda.items:
        table.add_row(item.name, format_td(item.duration, positive_sign=False))
    return table


def render_running_agenda(agenda: Agenda, show_delta_for="previous+current") -> Table:
    """Render a table for a currently running agenda."""
    table = _get_empty_table(agenda.title)
    for row_idx, item in enumerate(agenda.items):
        name = item.name
        time = item.delta
        plan = format_td(item.duration, positive_sign=False)

        if row_idx < agenda.current_item_idx:  # previous item
            name = f"[dim]{name}"
            plan = f"[dim]{plan}"
            # show delta
            # time += agenda.delta_for(row_idx)
            # time = f"[dim]{format_td(time)}"
            # show logged worktime
            if item.worktime < timedelta(seconds=3):
                time = ""
            else:
                time = f"[dim]{format_td(item.worktime, positive_sign=False)}"
        elif row_idx == agenda.current_item_idx:  # active item
            name = f"[b]{name}"
            plan = f"[b]{plan}"
            # show delta
            time += agenda.delta
            time = f"[b]{format_td(-time)}"
            # show current worktime
            # time = f"[dim]{format_td(item.worktime, positive_sign=False)}"
        else:  # upcoming item
            name = f"[dim]{name}"
            plan = f"[dim]{plan}"
            if item.worktime < timedelta(seconds=5):
                time = ""
            else:
                time = f"[dim]{format_td(item.worktime, positive_sign=False)}"

        # highlight items that exceed planned time by specific amount
        if item.delta < -timedelta(seconds=30):
            time = f"[red]{time}"

        table.add_row(name, plan, time)
    return table


def render_completed_agenda(agenda: Agenda) -> Table:
    """Render table for a previously completed agenda."""
    table = _get_empty_table(agenda.title)
    for item in agenda.items:
        name = f"{item.name}"
        plan = f"{format_td(item.duration, positive_sign=False)}"
        time = f"{format_td(item.worktime, positive_sign=False)}"
        table.add_row(name, plan, time)
    return table
