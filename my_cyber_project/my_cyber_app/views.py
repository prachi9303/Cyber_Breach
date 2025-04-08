import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from my_cyber_project.settings import BASE_DIR
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create a user if not already exists
if not User.objects.filter(username='prachi').exists():
    User.objects.create_user('prachi', password='prachi123')
else:
    print("User with this username already exists.")


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('upload_file')  # Redirect to upload page after successful login
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            upload_dir = os.path.join(BASE_DIR, 'media', 'uploads')

            try:
                # Create uploads directory if not exists
                os.makedirs(upload_dir, exist_ok=True)

                fs = FileSystemStorage(location=upload_dir)
                filename = fs.save(file.name, file)
                request.session['uploaded_filename'] = filename  # Store filename in session
                return redirect('data_analysis', filename=filename)  # Redirect to data analysis

            except Exception as e:
                print(f"Error while saving the file: {e}")
                return render(request, 'upload.html', {'error': 'Failed to upload file. Please try again.'})

    return render(request, 'upload.html')


@login_required
def data_analysis(request, filename):
    file_path = os.path.join(BASE_DIR, 'media', 'uploads', filename)

    # Check if file exists
    if not os.path.exists(file_path):
        return render(request, 'analysis.html', {'error': 'Uploaded file not found.'})

    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Data Analysis
        total_records = df.shape[0]
        unique_companies = df['Company'].nunique()

        # Create bar chart
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='Breach Type', palette='viridis')
        plt.title('Breach Type Count')
        plt.xticks(rotation=45)
        bar_chart_path = os.path.join(BASE_DIR, 'media', 'static', 'breach_type_count.png')
        plt.tight_layout()
        plt.savefig(bar_chart_path)
        plt.close()

        # Create spline chart if 'Date' column exists
        if 'Date' in df.columns:
            df['Year'] = pd.to_datetime(df['Date'], errors='coerce').dt.year
            records_exposed_over_years = df.groupby('Year')['Records Exposed'].sum()
            plt.figure(figsize=(10, 6))
            records_exposed_over_years.plot(kind='line')
            plt.title('Records Exposed Over Years')
            spline_chart_path = os.path.join(BASE_DIR, 'media', 'static', 'records_exposed_over_years.png')
            plt.savefig(spline_chart_path)
            plt.close()
        else:
            print("Date column not found.")

        return render(request, 'analysis.html', {
            'total_records': total_records,
            'unique_companies': unique_companies,
            'image_url': '/media/static/breach_type_count.png',
            'spline_image_url': '/media/static/records_exposed_over_years.png',
            'analysis': df.describe().to_html(),
        })
    except Exception as e:
        print(f"Error while reading the CSV file: {e}")
        return render(request, 'analysis.html', {'error': 'Failed to analyze data. Please check the file format.'})


@login_required
def malware_analysis(request):
    file_path = os.path.join(BASE_DIR, 'media', 'uploads', request.session.get('uploaded_filename', ''))
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        # Initialize counts and lists for messages
        hacked_count = 0
        poor_security_count = 0
        secured_count = 0
        hacked_links = []
        poor_security_links = []
        secured_links = []

        if 'Breach Type' in df.columns and 'Source Link' in df.columns:
            for index, row in df.iterrows():
                breach_type = row['Breach Type']
                source_link = row['Source Link']

                if breach_type == 'hacked':
                    hacked_count += 1
                    hacked_links.append(source_link)
                elif breach_type == 'poor security':
                    poor_security_count += 1
                    poor_security_links.append(source_link)
                elif breach_type == 'secured':
                    secured_count += 1
                    secured_links.append(source_link)

            # Prepare messages based on the counts
            messages = {
                'hacked': f"There are {hacked_count} instances of hacked breaches. Links: {', '.join(hacked_links)}" if hacked_count > 0 else "No hacked breaches found.",
                'poor_security': f"There are {poor_security_count} instances of poor security. Improve the security for these links: {', '.join(poor_security_links)}" if poor_security_count > 0 else "No poor security breaches found.",
                'secured': f"There are {secured_count} instances that are secure." if secured_count > 0 else "No secured breaches found."
            }

        else:
            messages = {
                'error': "The required columns 'Breach Type' or 'Source Link' are not found in the CSV file."
            }

    else:
        messages = {
            'error': "No file found for analysis."
        }

    return render(request, 'malware_analysis.html', {
        'messages': messages,
        'malware_count': hacked_count + poor_security_count + secured_count,  # Total breaches analyzed
        'hacked_links': hacked_links,  # List of hacked links
        'poor_security_links': poor_security_links,  # List of poor security links
        'secured_links': secured_links,  # List of secured links
        'message': 'Malware analysis complete.',
    })




@login_required
def unmalware_analysis(request):
    file_path = os.path.join(BASE_DIR, 'media', 'uploads', request.session.get('uploaded_filename', ''))
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        unmalware_count = df['Unmalware Indicator'].sum() if 'Unmalware Indicator' in df.columns else 0
    else:
        unmalware_count = "No file found for analysis."

    return render(request, 'unmalware_analysis.html', {
        'message': 'Unmalware analysis complete.',
    })


@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')  # Redirect to login page


def check_link(request):
    return None