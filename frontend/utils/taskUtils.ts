import { parseISO, isToday, isPast, isFuture } from 'date-fns';

export interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string;
  assignedToName: string;
  assignedBy: string;
  assignedByName: string;
  deadline: string;
  priority: string;
  department: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}

export const isOverdue = (deadline: string): boolean => {
  return isPast(parseISO(deadline)) && !isToday(parseISO(deadline));
};

export const isDueToday = (deadline: string): boolean => {
  return isToday(parseISO(deadline));
};

export const sortTasks = (tasks: Task[]): Task[] => {
  return [...tasks].sort((a, b) => {
    // First: Overdue tasks
    const aOverdue = isOverdue(a.deadline);
    const bOverdue = isOverdue(b.deadline);
    if (aOverdue && !bOverdue) return -1;
    if (!aOverdue && bOverdue) return 1;

    // Second: Due today
    const aDueToday = isDueToday(a.deadline);
    const bDueToday = isDueToday(b.deadline);
    if (aDueToday && !bDueToday) return -1;
    if (!aDueToday && bDueToday) return 1;

    // Third: Priority
    const priorityOrder = { High: 1, Medium: 2, Low: 3 };
    const aPriority = priorityOrder[a.priority as keyof typeof priorityOrder];
    const bPriority = priorityOrder[b.priority as keyof typeof priorityOrder];
    if (aPriority !== bPriority) return aPriority - bPriority;

    // Finally: Deadline
    return parseISO(a.deadline).getTime() - parseISO(b.deadline).getTime();
  });
};

export const groupTasks = (tasks: Task[]) => {
  const completed = tasks.filter((t) => t.status === 'Completed');
  const pending = tasks.filter((t) => t.status !== 'Completed');

  const urgentToday = pending.filter(
    (t) => isOverdue(t.deadline) || isDueToday(t.deadline)
  );

  const upcoming = pending.filter(
    (t) => !isOverdue(t.deadline) && !isDueToday(t.deadline)
  );

  return {
    urgentToday: sortTasks(urgentToday),
    upcoming: sortTasks(upcoming),
    completed: sortTasks(completed),
  };
};