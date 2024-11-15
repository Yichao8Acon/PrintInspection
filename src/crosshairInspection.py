import Tools
import cv2 as cv
import numpy as np


class CrossHairInspection:

    def __init__(self):
        self.roi_range = [0, 0, 550, 1000]
        self.search_area1 = [110, 0, 100, 1000]  # vertical edge
        self.search_area2 = [0, 50, 450, 30]  # horizontal edge
        self.search_area3 = [900, 400, 50, 500]  # vertical crosshair line
        self.search_area4 = [600, 600, 200, 100]  # horizontal crosshair line
        self.num_lines = 10

    def main(self, img):
        height, width = img.shape[:2]
        self.search_area1[3] = height
        self.search_area2[3] = width
        img_copy = img.copy()
        # Find vertical edge
        processed = self.preprocess(img)
        transition = self.find_transitions(processed, self.search_area1)
        slope, intercept = self.fit_regression_line(transition, 'vertical')
        for x, y in transition:
            cv.circle(img_copy, (x, y), 3, (0, 255, 0), -1)
        cv.rectangle(img_copy, self.search_area1, (0, 0, 255), 4)

        # TODO error prevention

        # start_x, start_y, end_x, end_y = self.compute_detected_line(img, transition, slope, intercept, 'vertical')
        # cv.line(img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 3)
        return img_copy

    def get_ROI(self, img):
        img = Tools.crop_roi(img, *self.roi_range)
        return img

    def preprocess(self, img):
        img = self.get_ROI(img)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(img, (5, 5), 0)
        kernel = np.ones((5, 5), np.uint8)
        closed = cv.morphologyEx(blurred, cv.MORPH_CLOSE, kernel)
        return closed

    def find_transitions(self, img, search_area, search_dir='horizontal'):
        x, y, w, h = search_area
        transitions = []  # Store transition points

        line_step = 1  # Each line will be 1 pixel
        for i in range(self.num_lines):
            # Step 1: Calculate the step for each line (1 pixel)
            line_y = y + (i * (h // self.num_lines))  # Calculate the y position of the line
            line_x = x + (i * (w // self.num_lines))  # Calculate the x position of the line

            # Step 2: Extract the line (1 pixel height)
            line = img[line_y:line_y + line_step, x:x + w]  # Extract the line
            if search_dir == 'vertical':
                line = img[y:y + h, line_x:line_x + line_step]

            # Step 3: Convert to grayscale if the image is not already
            gray_line = cv.cvtColor(line, cv.COLOR_BGR2GRAY) if len(line.shape) == 3 else line

            # Step 4: Threshold to create a binary image
            _, binary_line = cv.threshold(gray_line, 127, 255, cv.THRESH_BINARY)

            # Step 5: Find transitions
            transition_indices = np.where(np.diff(binary_line.flatten()) != 0)[0]
            if search_dir == 'horizontal' and len(transition_indices) > 0:
                # Get the x position of transitions relative to the original image
                transitions.extend([(x + transition_index, line_y) for transition_index in transition_indices])
            if search_dir == 'vertical' and len(transition_indices) > 0:
                # Get the y position of transitions relative to the original image
                transitions.extend([(line_x, y + transition_index) for transition_index in transition_indices])
        return transitions

    def fit_regression_line(self, points, orientation="horizontal"):
        if len(points) == 0:
            return None, None  # No points to fit

        # Convert to numpy arrays for regression
        x_points, y_points = zip(*points)
        x_points = np.array(x_points)
        y_points = np.array(y_points)
        if orientation == "horizontal":
            # Fit line in y = mx + c form for horizontal orientation
            slope, intercept = np.polyfit(x_points, y_points, 1)
        elif orientation == "vertical":
            # Fit line in x = my + c form for vertical orientation
            slope, intercept = np.polyfit(y_points, x_points, 1)
        return slope, intercept

    def compute_detected_line(self, img, transitions, slope, intercept, orientation="horizontal"):
        if orientation == "horizontal":
            start_x = 0
            start_y = transitions[0][1]
            end_x = img.shape[1]
            end_y = int(slope * end_x + intercept)

        if orientation == "vertical":
            start_x = transitions[0][0]
            start_y = 0
            end_y = img.shape[0]
            end_x = int(slope * end_y + intercept)
        return start_x, start_y, end_x, end_y

    def plot_results(self, img, transitions, slopes, intercepts):
        # Draw the original image and the transition points
        img_copy = img.copy()
        for index, [transition, orientation] in enumerate(transitions):
            # Mark the transition points
            if len(transition) == 0: continue
            for x, y in transition:
                cv.circle(img_copy, (x, y), 3, (0, 255, 0), -1)  # Mark transition points
            start_x, start_y, end_x, end_y = self.compute_detected_line(img, transition, slopes[index],
                                                                        intercepts[index], orientation)
            cv.line(img_copy, (start_x, start_y), (end_x, end_y), (0, 255, 0), 3)
        return img_copy
        # Show the result
        # plt.imshow(cv.cvtColor(img_copy, cv.COLOR_BGR2RGB))
        # plt.title('Detected Transitions and Fitted Line')
        # plt.axis('off')
        # plt.show()
