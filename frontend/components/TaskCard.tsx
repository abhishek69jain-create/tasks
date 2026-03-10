import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { format } from 'date-fns';
import { PRIORITY_COLORS, STATUS_COLORS } from '../utils/constants';
import { isOverdue, isDueToday } from '../utils/taskUtils';

interface TaskCardProps {
  task: any;
  onPress: () => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onPress }) => {
  const priorityColor = PRIORITY_COLORS[task.priority as keyof typeof PRIORITY_COLORS];
  const statusColor = STATUS_COLORS[task.status as keyof typeof STATUS_COLORS];
  const overdue = isOverdue(task.deadline);
  const dueToday = isDueToday(task.deadline);

  return (
    <TouchableOpacity style={[styles.card, { borderLeftColor: priorityColor }]} onPress={onPress}>
      <View style={styles.header}>
        <Text style={styles.title} numberOfLines={1}>
          {task.title}
        </Text>
        <View style={[styles.priorityBadge, { backgroundColor: priorityColor }]}>
          <Text style={styles.priorityText}>{task.priority}</Text>
        </View>
      </View>

      <Text style={styles.description} numberOfLines={2}>
        {task.description}
      </Text>

      <View style={styles.info}>
        <View style={styles.infoRow}>
          <Ionicons name="person-outline" size={14} color="#64748B" />
          <Text style={styles.infoText}>{task.assignedToName}</Text>
        </View>
        <View style={styles.infoRow}>
          <Ionicons name="briefcase-outline" size={14} color="#64748B" />
          <Text style={styles.infoText}>{task.department}</Text>
        </View>
      </View>

      <View style={styles.footer}>
        <View style={styles.deadlineContainer}>
          <Ionicons
            name="calendar-outline"
            size={14}
            color={overdue ? '#EF4444' : dueToday ? '#F59E0B' : '#64748B'}
          />
          <Text
            style={[
              styles.deadline,
              overdue && styles.overdue,
              dueToday && styles.dueToday,
            ]}
          >
            {format(new Date(task.deadline), 'MMM dd, yyyy h:mm a')}
          </Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
          <Text style={styles.statusText}>{task.status}</Text>
        </View>
      </View>

      {overdue && (
        <View style={styles.overdueFlag}>
          <Ionicons name="alert-circle" size={12} color="#fff" />
          <Text style={styles.overdueFlagText}>OVERDUE</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0F172A',
    flex: 1,
    marginRight: 8,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  priorityText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  description: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 12,
    lineHeight: 20,
  },
  info: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  infoText: {
    fontSize: 12,
    color: '#64748B',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deadlineContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  deadline: {
    fontSize: 12,
    color: '#64748B',
  },
  overdue: {
    color: '#EF4444',
    fontWeight: '600',
  },
  dueToday: {
    color: '#F59E0B',
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '500',
  },
  overdueFlag: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: '#EF4444',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderTopRightRadius: 12,
    borderBottomLeftRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  overdueFlagText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
});