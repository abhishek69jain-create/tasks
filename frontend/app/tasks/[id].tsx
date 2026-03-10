import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { format } from 'date-fns';
import { taskService, commentService, attachmentService } from '../../services/api';
import { PRIORITY_COLORS, STATUS_COLORS } from '../../utils/constants';
import { useAuth } from '../../context/AuthContext';
import { isOverdue, isDueToday } from '../../utils/taskUtils';

export default function TaskDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const { user, isAdmin } = useAuth();
  const [task, setTask] = useState<any>(null);
  const [comments, setComments] = useState<any[]>([]);
  const [attachments, setAttachments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadTaskDetails();
  }, [id]);

  const loadTaskDetails = async () => {
    try {
      setLoading(true);
      const [taskData, commentsData, attachmentsData] = await Promise.all([
        taskService.getTask(id as string),
        commentService.getComments(id as string),
        attachmentService.getAttachments(id as string),
      ]);
      setTask(taskData);
      setComments(commentsData);
      setAttachments(attachmentsData);
    } catch (error) {
      console.error('Error loading task details:', error);
      Alert.alert('Error', 'Failed to load task details');
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    setSubmitting(true);
    try {
      const comment = await commentService.createComment(id as string, newComment.trim());
      setComments([...comments, comment]);
      setNewComment('');
    } catch (error) {
      Alert.alert('Error', 'Failed to add comment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleMarkComplete = async () => {
    try {
      const updated = await taskService.updateTask(id as string, { status: 'Completed' });
      setTask(updated);
      Alert.alert('Success', 'Task marked as completed');
    } catch (error) {
      Alert.alert('Error', 'Failed to update task');
    }
  };

  const handlePickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant camera roll permissions');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      uploadFile(result.assets[0]);
    }
  };

  const handlePickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: '*/*',
        copyToCacheDirectory: true,
      });

      if (!result.canceled) {
        uploadFile(result.assets[0]);
      }
    } catch (error) {
      console.error('Error picking document:', error);
    }
  };

  const uploadFile = async (file: any) => {
    try {
      const attachment = await attachmentService.uploadAttachment(id as string, {
        uri: file.uri,
        name: file.fileName || 'file',
        type: file.mimeType || 'application/octet-stream',
      });
      setAttachments([...attachments, attachment]);
      Alert.alert('Success', 'File uploaded successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to upload file');
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  if (!task) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Task not found</Text>
      </View>
    );
  }

  const priorityColor = PRIORITY_COLORS[task.priority as keyof typeof PRIORITY_COLORS];
  const statusColor = STATUS_COLORS[task.status as keyof typeof STATUS_COLORS];
  const overdue = isOverdue(task.deadline);
  const dueToday = isDueToday(task.deadline);

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color="#0F172A" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Task Details</Text>
          <View style={{ width: 24 }} />
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Task Info */}
          <View style={styles.card}>
            <View style={styles.taskHeader}>
              <Text style={styles.taskTitle}>{task.title}</Text>
              {overdue && (
                <View style={styles.overdueTag}>
                  <Ionicons name="alert-circle" size={16} color="#fff" />
                  <Text style={styles.overdueText}>OVERDUE</Text>
                </View>
              )}
            </View>

            <Text style={styles.description}>{task.description}</Text>

            <View style={styles.badges}>
              <View style={[styles.badge, { backgroundColor: priorityColor }]}>
                <Text style={styles.badgeText}>{task.priority}</Text>
              </View>
              <View style={[styles.badge, { backgroundColor: statusColor }]}>
                <Text style={styles.badgeText}>{task.status}</Text>
              </View>
              <View style={[styles.badge, { backgroundColor: '#64748B' }]}>
                <Text style={styles.badgeText}>{task.department}</Text>
              </View>
            </View>

            <View style={styles.divider} />

            <View style={styles.infoRow}>
              <Ionicons name="person-outline" size={20} color="#64748B" />
              <View style={styles.infoContent}>
                <Text style={styles.infoLabel}>Assigned To</Text>
                <Text style={styles.infoValue}>{task.assignedToName}</Text>
              </View>
            </View>

            <View style={styles.infoRow}>
              <Ionicons name="person-add-outline" size={20} color="#64748B" />
              <View style={styles.infoContent}>
                <Text style={styles.infoLabel}>Assigned By</Text>
                <Text style={styles.infoValue}>{task.assignedByName}</Text>
              </View>
            </View>

            <View style={styles.infoRow}>
              <Ionicons
                name="calendar-outline"
                size={20}
                color={overdue ? '#EF4444' : dueToday ? '#F59E0B' : '#64748B'}
              />
              <View style={styles.infoContent}>
                <Text style={styles.infoLabel}>Deadline</Text>
                <Text
                  style={[
                    styles.infoValue,
                    overdue && styles.overdueText2,
                    dueToday && styles.dueTodayText,
                  ]}
                >
                  {format(new Date(task.deadline), 'MMM dd, yyyy h:mm a')}
                </Text>
              </View>
            </View>

            {task.status !== 'Completed' && (
              <TouchableOpacity style={styles.completeButton} onPress={handleMarkComplete}>
                <Ionicons name="checkmark-circle" size={24} color="#fff" />
                <Text style={styles.completeButtonText}>Mark as Complete</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Attachments */}
          <View style={styles.card}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Attachments ({attachments.length})</Text>
              <View style={styles.uploadButtons}>
                <TouchableOpacity style={styles.iconButton} onPress={handlePickImage}>
                  <Ionicons name="image-outline" size={24} color="#3B82F6" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.iconButton} onPress={handlePickDocument}>
                  <Ionicons name="document-outline" size={24} color="#3B82F6" />
                </TouchableOpacity>
              </View>
            </View>

            {attachments.map((attachment) => (
              <View key={attachment.id} style={styles.attachmentItem}>
                <Ionicons name="document-attach" size={20} color="#64748B" />
                <View style={styles.attachmentInfo}>
                  <Text style={styles.attachmentName}>{attachment.fileName}</Text>
                  <Text style={styles.attachmentMeta}>
                    by {attachment.uploadedByName} •{' '}
                    {format(new Date(attachment.createdAt), 'MMM dd, yyyy')}
                  </Text>
                </View>
              </View>
            ))}

            {attachments.length === 0 && (
              <Text style={styles.emptyText}>No attachments yet</Text>
            )}
          </View>

          {/* Comments */}
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Comments ({comments.length})</Text>

            <View style={styles.commentInput}>
              <TextInput
                style={styles.input}
                placeholder="Add a comment..."
                value={newComment}
                onChangeText={setNewComment}
                multiline
              />
              <TouchableOpacity
                style={[styles.sendButton, !newComment.trim() && styles.sendButtonDisabled]}
                onPress={handleAddComment}
                disabled={submitting || !newComment.trim()}
              >
                <Ionicons name="send" size={20} color="#fff" />
              </TouchableOpacity>
            </View>

            {comments.map((comment) => (
              <View key={comment.id} style={styles.comment}>
                <View style={styles.commentHeader}>
                  <Text style={styles.commentAuthor}>{comment.userName}</Text>
                  <Text style={styles.commentTime}>
                    {format(new Date(comment.createdAt), 'MMM dd, h:mm a')}
                  </Text>
                </View>
                <Text style={styles.commentText}>{comment.text}</Text>
              </View>
            ))}

            {comments.length === 0 && (
              <Text style={styles.emptyText}>No comments yet</Text>
            )}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0F172A',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  taskTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0F172A',
    flex: 1,
    marginRight: 12,
  },
  overdueTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EF4444',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    gap: 4,
  },
  overdueText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
  description: {
    fontSize: 16,
    color: '#64748B',
    lineHeight: 24,
    marginBottom: 16,
  },
  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16,
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  divider: {
    height: 1,
    backgroundColor: '#E2E8F0',
    marginVertical: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    color: '#0F172A',
    fontWeight: '500',
  },
  overdueText2: {
    color: '#EF4444',
  },
  dueTodayText: {
    color: '#F59E0B',
  },
  completeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#10B981',
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 16,
    gap: 8,
  },
  completeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 12,
  },
  uploadButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 8,
    backgroundColor: '#EFF6FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  attachmentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  attachmentInfo: {
    flex: 1,
  },
  attachmentName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#0F172A',
    marginBottom: 2,
  },
  attachmentMeta: {
    fontSize: 12,
    color: '#64748B',
  },
  emptyText: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
    paddingVertical: 12,
  },
  commentInput: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  input: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#0F172A',
    maxHeight: 100,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 8,
    backgroundColor: '#3B82F6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  comment: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  commentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  commentAuthor: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0F172A',
  },
  commentTime: {
    fontSize: 12,
    color: '#94A3B8',
  },
  commentText: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
  },
});
