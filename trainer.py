import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
import os
import time
from tqdm import tqdm
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from utils import colored_print


class VideoTraining:
    def __init__(self, model, model_name, train_loader, test_loader, validation_loader, num_epochs, criterion, optimizer, device, project_name, checkpoint_interval=None, weight_decay=1e-4):
        """
        Initializes the VideoTraining class.
        """
        self.model = model
        self.model_name = model_name
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.validation_loader = validation_loader
        self.num_epochs = num_epochs
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.project_name = project_name
        self.checkpoint_interval = checkpoint_interval
        self.weight_decay = weight_decay
        
        # Initialize lists to store metrics after each epoch
        self.train_losses = []
        self.test_losses = []
        self.validation_losses = []
        self.train_accuracy = []
        self.test_accuracy = []
        self.validation_accuracy = []
        self.test_precision = []
        self.validation_precision = []
        self.test_recall = []
        self.validation_recall = []
        self.test_f1 = []
        self.validation_f1 = []

        # Create a directory to save trained models within the project directory
        self.project_dir = os.path.join('trained_models', self.project_name)
        os.makedirs(self.project_dir, exist_ok=True)

        # Learning rate scheduler
        self.scheduler = StepLR(self.optimizer, step_size=30, gamma=0.1)

        if self.checkpoint_interval is None:
            if self.model_name == 'vvt':
                self.checkpoint_interval = 25
            else:
                self.checkpoint_interval = 5

    def train(self):
        """
        Trains the model for the specified number of epochs.
        """
        start_time = time.time()

        for epoch in range(self.num_epochs):
            self.model.train()
            running_loss = 0.0
            correct_batch = 0
            total_batch = 0

            train_loader_with_progress = tqdm(self.train_loader, desc=f'Epoch [{epoch+1}/{self.num_epochs}] (training)', position=0, leave=True)

            for videos, labels in train_loader_with_progress:
                videos = videos.to(self.device)
                labels = labels.to(self.device)

                self.optimizer.zero_grad()
                outputs = self.model(videos)
                loss = self.criterion(outputs, labels)

                # Apply L2 regularization
                l2_regularization = sum(torch.norm(param, p=2) ** 2 for param in self.model.parameters())
                loss += 0.5 * self.weight_decay * l2_regularization  # 0.5 * weight_decay * ||w||^2

                loss.backward()

                self.optimizer.step()

                running_loss += loss.item()

                _, predicted_batch = outputs.max(1)
                total_batch += labels.size(0)
                correct_batch += predicted_batch.eq(labels).sum().item()

                train_loader_with_progress.set_postfix({'Train Loss (Batch)': loss.item(),
                                                        'Train Acc (Batch)': 100. * correct_batch / total_batch,
                                                        'Train Loss': running_loss / len(self.train_loader)})

            epoch_accuracy = 100. * correct_batch / total_batch
            train_loader_with_progress.set_postfix({'Train Loss': running_loss / len(self.train_loader), 'Train Acc': epoch_accuracy})

            self.train_losses.append(running_loss / len(self.train_loader))
            self.train_accuracy.append(100. * correct_batch / total_batch)

            # Conduct test and log metrics
            avg_test_loss, test_accuracy, test_precision, test_recall, test_f1, _, _ = self.test(epoch)
            self.test_losses.append(avg_test_loss)
            self.test_accuracy.append(test_accuracy)
            self.test_precision.append(test_precision)
            self.test_recall.append(test_recall)
            self.test_f1.append(test_f1)

            # Conduct validation and log metrics
            avg_validation_loss, validation_accuracy, validation_precision, validation_recall, validation_f1, _, _ = self.validate(epoch)
            self.validation_losses.append(avg_validation_loss)
            self.validation_accuracy.append(validation_accuracy)
            self.validation_precision.append(validation_precision)
            self.validation_recall.append(validation_recall)
            self.validation_f1.append(validation_f1)

            # Print train, test, and validation metrics
            print(f"Epoch [{epoch+1}/{self.num_epochs}]")
            print("{:<20} {:<20} {:<20}".format("", "Loss", "Accuracy", "Precision", "Recall", "F1-Score"))
            print("{:<20} {:<20.4f} {:<20.3f}% {:<20.3f} {:<20.3f} {:<20.3f}".format("Train", running_loss / len(self.train_loader), epoch_accuracy, _, _, _))
            print("{:<20} {:<20.4f} {:<20.3f}% {:<20.3f} {:<20.3f} {:<20.3f}".format("Test", avg_test_loss, test_accuracy, test_precision, test_recall, test_f1))
            print("{:<20} {:<20.4f} {:<20.3f}% {:<20.3f} {:<20.3f} {:<20.3f}".format("Validation", avg_validation_loss, validation_accuracy, validation_precision, validation_recall, validation_f1))
            print()  # Add a newline for spacing between epochs

            # Save checkpoint if needed
            if (epoch + 1) % self.checkpoint_interval == 0 or epoch == self.num_epochs - 1:
                self.save_checkpoint(epoch)

            # Step the learning rate scheduler
            self.scheduler.step()

        end_time = time.time()
        total_training_time = end_time - start_time

        losses_dict = {
            'Train': {
                'Loss': self.train_losses,
                'Accuracy': self.train_accuracy
            },
            'Test': {
                'Loss': self.test_losses,
                'Accuracy': self.test_accuracy,
                'Precision': self.test_precision,
                'Recall': self.test_recall,
                'F1-Score': self.test_f1
            },
            'Validation': {
                'Loss': self.validation_losses,
                'Accuracy': self.validation_accuracy,
                'Precision': self.validation_precision,
                'Recall': self.validation_recall,
                'F1-Score': self.validation_f1
            },
            'Training Time': total_training_time
        }

        return losses_dict


    def test(self, epoch):
        """
        Tests the model on the test dataset and computes additional evaluation metrics.

        Parameters:
        - epoch: Current epoch number.
        """
        self.model.eval()
        test_loss = 0.0
        correct = 0
        total = 0
        false_positives = 0
        false_negatives = 0

        with torch.no_grad():
            test_loader_with_progress = tqdm(self.test_loader, desc=f'Epoch [{epoch+1}/{self.num_epochs}] (testing)', position=0, leave=True)

            all_labels = []
            all_predicted = []

            for videos, labels in test_loader_with_progress:
                videos = videos.to(self.device)
                labels = labels.to(self.device)
                outputs = self.model(videos)
                loss = self.criterion(outputs, labels)
                test_loss += loss.item()

                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

                all_labels.extend(labels.cpu().numpy())
                all_predicted.extend(predicted.cpu().numpy())

                test_loader_with_progress.set_postfix({'Test Loss': test_loss / len(self.test_loader),
                                                    'Test Acc': 100. * correct / total})

            avg_test_loss = test_loss / len(self.test_loader)

            # Calculate metrics using sklearn functions
            precision, recall, f1, _= precision_recall_fscore_support(all_labels, all_predicted, average='binary', zero_division=0)

            return avg_test_loss, 100. * correct / total, precision, recall, f1, false_positives, false_negatives


    def validate(self, epoch):
        """
        Validates the model on the validation dataset and computes additional evaluation metrics.

        Parameters:
        - epoch: Current epoch number.
        """
        self.model.eval()
        validation_loss = 0.0
        correct = 0
        total = 0
        false_positives = 0
        false_negatives = 0

        with torch.no_grad():
            validation_loader_with_progress = tqdm(self.validation_loader, desc=f'Epoch [{epoch+1}/{self.num_epochs}] (validating)', position=0, leave=True)

            all_labels = []
            all_predicted = []

            for videos, labels in validation_loader_with_progress:
                videos = videos.to(self.device)
                labels = labels.to(self.device)
                outputs = self.model(videos)
                loss = self.criterion(outputs, labels)
                validation_loss += loss.item()

                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

                all_labels.extend(labels.cpu().numpy())
                all_predicted.extend(predicted.cpu().numpy())

                validation_loader_with_progress.set_postfix({'Validation Loss': validation_loss / len(self.validation_loader),
                                                    'Validation Acc': 100. * correct / total})

            avg_validation_loss = validation_loss / len(self.validation_loader)

            # Calculate metrics using sklearn functions
            precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_predicted, average='binary', zero_division=0)

            return avg_validation_loss, 100. * correct / total, precision, recall, f1, false_positives, false_negatives


        
    def save_checkpoint(self, epoch):
        """
        Saves a checkpoint of the model and optimizer.

        Parameters:
        - epoch: Current epoch number.
        """
        checkpoint_path = os.path.join(self.project_dir, f'{self.model_name}_checkpoint_epoch{epoch + 1}.pt')
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, checkpoint_path)
        colored_print(f"Checkpoint saved at epoch {epoch+1}", color_code=36)


    def cleanup(self):
            """
            Releases all resources.
            """
            del self.model
            del self.train_loader
            del self.test_loader
            del self.validation_loader
            del self.criterion
            del self.optimizer
