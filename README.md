# OMR-scanning-and-test-grading
We use computer vision and image processing techniques to build this OMR sheet grader. In this program we first scan the OMR sheet using openCv and python. there after we perform contour sorting and perspective transforms.
Steps:
Detect the exam in an image.
Apply a perspective transform to extract the top-down, birds-eye-view of the exam.
Extract the set of bubbles (i.e., the possible answer choices) from the perspective transformed exam.
Sort the questions/bubbles into rows.
By using maximum non-zero index count of each bubble in a row, we determine the marked (i.e., “bubbled in”) answer for each row.
Lookup the correct answer in our answer key to determine if the user was correct in their choice.
Repeat for all questions in the exam.
