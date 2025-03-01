FROM ultralytics/ultralytics:latest-cpu

# Copy the project folder
COPY . /home/people_counter

# Set environment variable to make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies from packages.txt
RUN apt-get update && \
    apt-get install ntp -y && \
    echo "System packages installed successfully!"

# Install Python dependencies from requirements.txt
RUN pip install firebase_admin && \
    echo "Python packages installed successfully!"

# Set the timezone to Asia/Colombo
RUN ln -fs /usr/share/zoneinfo/Asia/Colombo /etc/localtime && \
    echo "Asia/Colombo" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    echo "Timezone set to Asia/Colombo!"

# Set the working directory
WORKDIR /home/people_counter

# Start the Python scripts and write logs in append mode
CMD python3 People_count.py




# docker build -t people_counting:bootcamp .
# docker run -dt --name My_project -v D:\Coursers\BootCamp\week04\Assignment\project:/home/people_counter/configs  --restart always people_counting:bootcamp
# docker exec -it My_project /bin/bash
# docker logs -f My_project
# docker stop My_project

# docker tag people_counting:bootcamp ashannuwantha/people_counting:bootcamp
# docker push ashannuwantha/people_counting:bootcamp


