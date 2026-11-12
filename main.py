from bakery import assert_equal
from drafter import *
from dataclasses import dataclass

hide_debug_information()
set_website_title("Your Drafter Website")
set_website_framed(False)
set_site_information(author="Marissa Lolkema",
                     description="Final project submission for a student panning site that is meant to maximize time usage and balance of all activities", 
                     sources="Utilized ChatGPT as shown in Conversations with AI", 
                     planning= ["Copy of CSI Final Project 0_Pick a Problem(1)", "Copy of CSI Final Project 1_Design"],
                     links= ["https://mlolkema-sys.github.io/student_life_planners/?route=focus_timer"], 
                     server=None)

@dataclass
class Task:
    """Stores information about one academic or personal task."""

    name: str
    category: str
    duration: int
    deadline_day: str
    priority: str
    completed: bool
    scheduled_day: str
    scheduled_time: str


@dataclass
class State:
    """Stores information shared across the Student Life Planner."""

    tasks: list[Task]
    schedule: list[Task]
    selected_day: str
    study_duration: int
    break_duration: int
    timer_mode: str


def initial_state() -> State:
    """
    Creates the starting state for the application.

    Args:
        None

    Returns:
        State: The application state with default settings and empty lists.
    """
    return State(
        tasks=[],
        schedule=[],
        selected_day="Monday",
        study_duration=25,
        break_duration=5,
        timer_mode="study"
    )


def test_initial_state():
    """
    Tests that the application starts with the correct default values.

    Args:
        None

    Returns:
        None
    """
    assert_equal(initial_state(), State([], [], "Monday", 25, 5, "study"))
    assert_equal(initial_state().tasks, [])
    assert_equal(initial_state().schedule, [])


test_initial_state()


def calculate_priority(deadline_day: str, selected_day: str) -> str:
    """
    Assigns task priority based on how soon its deadline occurs.

    Args:
        deadline_day (str): The weekday when the task is due.
        selected_day (str): The weekday currently selected by the student.

    Returns:
        str: The priority level, either High, Medium, or Low.
    """
    weekdays = (
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    )

    if deadline_day not in weekdays or selected_day not in weekdays:
        return "Medium"

    days_until_deadline = (
        weekdays.index(deadline_day) - weekdays.index(selected_day)
    ) % 7

    if days_until_deadline <= 1:
        return "High"
    elif days_until_deadline <= 3:
        return "Medium"
    else:
        return "Low"


def test_calculate_priority():
    """
    Tests priority results for different deadline distances.

    Args:
        None

    Returns:
        None
    """
    assert_equal(calculate_priority("Monday", "Monday"), "High")
    assert_equal(calculate_priority("Wednesday", "Monday"), "Medium")
    assert_equal(calculate_priority("Friday", "Monday"), "Low")


test_calculate_priority()


@route
def index(state: State) -> Page:
    """
    Opens the home page when the application first starts.

    Args:
        state (State): The current application state.

    Returns:
        Page: The main Student Life Planner dashboard.
    """
    return home(state)


@route
def home(state: State) -> Page:
    """
    Displays the main dashboard and navigation buttons.

    Args:
        state (State): The current application state.

    Returns:
        Page: The dashboard with task totals and navigation buttons.
    """
    completed_count = 0

    for task in state.tasks:
        if task.completed:
            completed_count += 1

    return Page(state, [
        Header("Student Life Planner"),
        Text("Organize your schoolwork and personal responsibilities!"),
        Text("Total Tasks: " + str(len(state.tasks))),
        Text("Completed Tasks: " + str(completed_count)),
        Button("My Tasks", "my_tasks"),
        Button("Weekly Schedule", "weekly_schedule"),
        Button("Focus Timer", "focus_timer"),
        Button("Life Planner", "life_planner")
    ])


@route
def my_tasks(state: State) -> Page:
    """
    Displays all tasks and provides completion and deletion buttons.

    Args:
        state (State): The current application state.

    Returns:
        Page: A page showing tasks and their details.
    """
    page_content = [
        Header("My Tasks"),
        Button("Add a New Task", "new_task")
    ]

    if len(state.tasks) == 0:
        page_content.append(Text("You have not added any tasks yet."))

    for index, task in enumerate(state.tasks):
        if task.completed:
            status = "Completed"
        else:
            status = "Not Completed"

        page_content.append(Header(task.name, 3))
        page_content.append(Text("Category: " + task.category))
        page_content.append(Text("Duration: " + str(task.duration) + " minutes"))
        page_content.append(Text("Deadline: " + task.deadline_day))
        page_content.append(Text("Priority: " + task.priority))
        page_content.append(Text("Status: " + status))

        page_content.append(
            Button(
                "Mark Complete",
                "complete_task",
                [Argument("task_index", index)]
            )
        )

        page_content.append(
            Button(
                "Delete Task",
                "delete_task",
                [Argument("task_index", index)]
            )
        )

    page_content.append(Button("Home", "home"))

    return Page(state, page_content)


@route
def new_task(state: State) -> Page:
    """
    Displays the form used to create a new task.

    Args:
        state (State): The current application state.

    Returns:
        Page: A form for entering a task's information.
    """
    return Page(state, [
        Header("Add a New Task"),
        Text("Task Name:"),
        TextBox("task_name"),
        Text("Estimated Duration in Minutes:"),
        TextBox("duration", 30, "number"),
        Text("Task Category:"),
        SelectBox(
            "category",
            ["Academic", "Chore", "Personal"]
        ),
        Text("Deadline Day:"),
        SelectBox(
            "deadline_day",
            [
                "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"
            ]
        ),
        CheckBox("is_completed", False),
        Text("Check this box if the task is already completed."),
        Button("Save Task", "add_task")
    ])


@route
def add_task(
    state: State,
    task_name: str,
    duration: int,
    category: str,
    deadline_day: str,
    is_completed: bool
) -> Page:
    """
    Validates the form and adds a new Task to State.

    Args:
        state (State): The current application state.
        task_name (str): The name entered for the task.
        duration (int): The estimated time needed in minutes.
        category (str): The task category.
        deadline_day (str): The weekday when the task is due.
        is_completed (bool): Whether the task is already completed.

    Returns:
        Page: The task list or an error page if the input is invalid.
    """
    if task_name.strip() == "" or duration <= 0:
        return Page(state, [
            Header("Invalid Task"),
            Text("Enter a task name and a duration greater than zero."),
            Button("Return to Tasks", "my_tasks")
        ])

    priority = calculate_priority(
        deadline_day,
        state.selected_day
    )

    if category == "Personal" or category == "Chore":
        sched_day = deadline_day
        sched_time = "Due day"
    else:
        sched_day = "Not Scheduled"
        sched_time = "Not Scheduled"

    new_task = Task(
        name=task_name.strip(),
        category=category,
        duration=duration,
        deadline_day=deadline_day,
        priority=priority,
        completed=is_completed,
        scheduled_day=sched_day,
        scheduled_time=sched_time
    )

    state.tasks.append(new_task)

    if category == "Personal" or category == "Chore":
        state.schedule.append(new_task)

    return my_tasks(state)


def test_add_task():
    """
    Tests adding valid tasks and rejecting invalid task information.

    Args:
        None

    Returns:
        None
    """
    state_one = initial_state()
    add_task(state_one, "Biology Exam", 90, "Academic", "Monday", False)
    assert_equal(len(state_one.tasks), 1)
    assert_equal(state_one.tasks[0].priority, "High")

    state_two = initial_state()
    add_task(state_two, "   ", 30, "Personal", "Tuesday", False)
    assert_equal(len(state_two.tasks), 0)

    state_three = initial_state()
    add_task(state_three, "Laundry", 0, "Chore", "Friday", False)
    assert_equal(len(state_three.tasks), 0)


test_add_task()


@route
def complete_task(state: State, task_index: int) -> Page:
    """
    Marks the selected task as completed.

    Args:
        state (State): The current application state.
        task_index (int): The position of the task in the task list.

    Returns:
        Page: The updated task list.
    """
    if 0 <= task_index < len(state.tasks):
        state.tasks[task_index].completed = True

    return my_tasks(state)


def test_complete_task():
    """
    Tests completing tasks and handling invalid task positions.

    Args:
        None

    Returns:
        None
    """
    state_one = initial_state()
    state_one.tasks.append(
        Task("History Essay", "Academic", 60, "Wednesday",
             "Medium", False, "Not Scheduled", "Not Scheduled")
    )
    complete_task(state_one, 0)
    assert_equal(state_one.tasks[0].completed, True)

    state_two = initial_state()
    state_two.tasks.append(
        Task("Laundry", "Chore", 30, "Friday",
             "Low", False, "Not Scheduled", "Not Scheduled")
    )
    complete_task(state_two, 1)
    assert_equal(state_two.tasks[0].completed, False)

    state_three = initial_state()
    complete_task(state_three, 0)
    assert_equal(state_three.tasks, [])


test_complete_task()


@route
def delete_task(state: State, task_index: int) -> Page:
    """
    Removes the selected task from the task and schedule lists.

    Args:
        state (State): The current application state.
        task_index (int): The position of the task to remove.

    Returns:
        Page: The updated task list.
    """
    if 0 <= task_index < len(state.tasks):
        task_to_delete = state.tasks[task_index]
        del state.tasks[task_index]

        state.schedule = [
            task for task in state.schedule
            if task is not task_to_delete
        ]

    return my_tasks(state)


def test_delete_task():
    """
    Tests deleting tasks from both lists.

    Args:
        None

    Returns:
        None
    """
    state_one = initial_state()
    task = Task(
        "Laundry", "Chore", 30, "Friday", "Low",
        False, "Friday", "Due day"
    )
    state_one.tasks.append(task)
    state_one.schedule.append(task)
    delete_task(state_one, 0)
    assert_equal(len(state_one.tasks), 0)
    assert_equal(len(state_one.schedule), 0)

    state_two = initial_state()
    task = Task(
        "Study", "Academic", 45, "Tuesday", "High",
        False, "Tuesday", "Due day"
    )
    state_two.tasks.append(task)
    state_two.schedule.append(task)
    delete_task(state_two, 5)
    assert_equal(len(state_two.tasks), 1)
    assert_equal(len(state_two.schedule), 1)

    state_three = initial_state()
    delete_task(state_three, 0)
    assert_equal(len(state_three.tasks), 0)
    assert_equal(len(state_three.schedule), 0)


test_delete_task()


@route
def weekly_schedule(state: State) -> Page:
    """
    Displays personal and chore tasks scheduled for the selected day.

    Args:
        state (State): The current application state.

    Returns:
        Page: The schedule filtered for the currently selected weekday.
    """
    page_content = [
        Header("Weekly Schedule"),
        Header("Selected Day: " + state.selected_day, 3),
        Text("Showing Personal and Chore tasks due on " + state.selected_day + "."),
        Button("Change Selected Day", "select_day_form")
    ]

    found_task = False

    for task in state.schedule:
        if task.scheduled_day == state.selected_day and (task.category == "Personal" or task.category == "Chore"):
            found_task = True

            if task.completed:
                status = "Completed"
            else:
                status = "Needs to be done"

            page_content.append(
                Text(
                    task.name + " (" + task.category + ") | " +
                    str(task.duration) + " minutes | " +
                    task.priority + " Priority | " +
                    status
                )
            )

    if not found_task:
        page_content.append(Text("No personal or chore tasks scheduled for " + state.selected_day + "."))

    page_content.append(Button("Home", "home"))

    return Page(state, page_content)


@route
def select_day_form(state: State) -> Page:
    """
    Displays the form for choosing a schedule day.

    Args:
        state (State): The current application state.

    Returns:
        Page: A form for selecting a weekday.
    """
    return Page(state, [
        Header("Choose a Day"),
        SelectBox(
            "new_day",
            [
                "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"
            ],
            state.selected_day
        ),
        Button("Save Selected Day", "select_day")
    ])


@route
def select_day(state: State, new_day: str) -> Page:
    """
    Updates the day displayed on the weekly schedule.

    Args:
        state (State): The current application state.
        new_day (str): The weekday selected by the student.

    Returns:
        Page: The weekly schedule for the newly selected day.
    """
    state.selected_day = new_day

    return weekly_schedule(state)


def test_select_day():
    """
    Tests changing the selected weekday.

    Args:
        None

    Returns:
        None
    """
    state_one = initial_state()
    select_day(state_one, "Friday")
    assert_equal(state_one.selected_day, "Friday")

    state_two = initial_state()
    select_day(state_two, "Wednesday")
    assert_equal(state_two.selected_day, "Wednesday")

    state_three = initial_state()
    select_day(state_three, "Sunday")
    assert_equal(state_three.selected_day, "Sunday")


test_select_day()


@route
def focus_timer(state: State) -> Page:
    """
    Displays the study or break countdown timer.

    Args:
        state (State): The current application state.

    Returns:
        Page: The timer page with the active countdown.
    """
    if state.timer_mode == "study":
        current_duration = state.study_duration
    else:
        current_duration = state.break_duration

    return Page(state, [
        Header("Focus Timer"),
        Header("Current Mode: " + state.timer_mode),
        Text("Study Duration: " + str(state.study_duration) + " minutes"),
        Text("Break Duration: " + str(state.break_duration) + " minutes"),
        Text("The timer will automatically switch modes when it finishes."),
        Timer(
            current_duration * 60 * 1000,
            "timer_finished",
            controls=True
        ),
        Button("Switch Timer Mode", "change_timer_mode"),
        Button("Change Timer Settings", "timer_settings"),
        Button("Home", "home")
    ])


@route
def timer_finished(state: State) -> Page:
    """
    Switches the timer mode when a countdown finishes.

    Args:
        state (State): The current application state.

    Returns:
        Page: The timer page with the next countdown started.
    """
    if state.timer_mode == "study":
        state.timer_mode = "break"
    else:
        state.timer_mode = "study"

    return focus_timer(state)


def test_timer_finished():
    """
    Tests switching timer modes after a countdown finishes.

    Args:
        None

    Returns:
        None
    """
    state_one = initial_state()
    timer_finished(state_one)
    assert_equal(state_one.timer_mode, "break")

    state_two = initial_state()
    state_two.timer_mode = "break"
    timer_finished(state_two)
    assert_equal(state_two.timer_mode, "study")

    state_three = initial_state()
    state_three.timer_mode = "study"
    timer_finished(state_three)
    assert_equal(state_three.timer_mode, "break")


test_timer_finished()


@route
def timer_settings(state: State) -> Page:
    """
    Displays inputs for changing study and break durations.

    Args:
        state (State): The current application state.

    Returns:
        Page: A form for entering new timer durations.
    """
    return Page(state, [
        Header("Timer Settings"),
        Text("Study Duration in Minutes:"),
        TextBox("new_study_duration", state.study_duration, "number"),
        Text("Break Duration in Minutes:"),
        TextBox("new_break_duration", state.break_duration, "number"),
        Button("Save Timer Settings", "save_timer_settings")
    ])


@route
def save_timer_settings(
    state: State,
    new_study_duration: int,
    new_break_duration: int
) -> Page:
    """
    Updates study and break durations after validation.

    Args:
        state (State): The current application state.
        new_study_duration (int): The new study duration in minutes.
        new_break_duration (int): The new break duration in minutes.

    Returns:
        Page: The timer page with updated settings.
    """
    if new_study_duration > 0 and new_break_duration > 0:
        state.study_duration = new_study_duration
        state.break_duration = new_break_duration

    return focus_timer(state)


def test_save_timer_settings():
    """
    Tests saving valid timer settings and rejecting invalid settings.

    Args:
        None

    Returns:
        None
    """
    state_one = initial_state()
    save_timer_settings(state_one, 30, 10)
    assert_equal(state_one.study_duration, 30)
    assert_equal(state_one.break_duration, 10)

    state_two = initial_state()
    save_timer_settings(state_two, 0, 10)
    assert_equal(state_two.study_duration, 25)
    assert_equal(state_two.break_duration, 5)

    state_three = initial_state()
    save_timer_settings(state_three, 45, -5)
    assert_equal(state_three.study_duration, 25)
    assert_equal(state_three.break_duration, 5)


test_save_timer_settings()


@route
def change_timer_mode(state: State) -> Page:
    """
    Switches the timer between study and break modes.

    Args:
        state (State): The current application state.

    Returns:
        Page: The timer page showing the new mode.
    """
    if state.timer_mode == "study":
        state.timer_mode = "break"
    else:
        state.timer_mode = "study"

    return focus_timer(state)


def test_change_timer_mode():
    """
    Tests switching between study and break modes.

    Args:
        None

    Returns:
        None
    """
    state_one = initial_state()
    change_timer_mode(state_one)
    assert_equal(state_one.timer_mode, "break")

    state_two = initial_state()
    state_two.timer_mode = "break"
    change_timer_mode(state_two)
    assert_equal(state_two.timer_mode, "study")

    state_three = initial_state()
    state_three.timer_mode = "other"
    change_timer_mode(state_three)
    assert_equal(state_three.timer_mode, "study")


test_change_timer_mode()


@route
def life_planner(state: State) -> Page:
    """
    Displays unfinished responsibilities grouped by their due day.

    Args:
        state (State): The current application state.

    Returns:
        Page: A weekday list of unfinished tasks and responsibilities.
    """
    weekdays = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    page_content = [
        Header("Life Planner"),
        Text("Your Unfinished Responsibilities")
    ]

    for day in weekdays:
        page_content.append(Header(day, 3))

        found_task = False

        for task in state.tasks:
            if task.deadline_day == day and not task.completed:
                found_task = True

                page_content.append(
                    Text(
                        task.name + " - " +
                        task.category + " - " +
                        str(task.duration) + " minutes"
                    )
                )

                page_content.append(
                    Text("Priority: " + task.priority)
                )

        if not found_task:
            page_content.append(Text("Nothing due this day."))

    page_content.append(Button("My Tasks", "my_tasks"))
    page_content.append(Button("Home", "home"))

    return Page(state, page_content)


start_server(initial_state())
