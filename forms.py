from django import forms
from .models import Song

class SongSelectionForm(forms.Form):
    song = forms.ModelChoiceField(
        queryset=Song.objects.none(),
        label='Choose your favorite song',
        widget=forms.Select(attrs={'class': 'song-select'})
    )

    def __init__(self, *args, **kwargs):
        print("Initializing SongSelectionForm")
        
        super(SongSelectionForm, self).__init__(*args, **kwargs)

        if self.is_bound and'song'in self.data:
            try:
                song_id = int(self.data.get('song'))
                print(f"Song ID from data: {song_id}")  
                self.fields['song'].queryset = Song.objects.filter(id=song_id)
            except (ValueError, TypeError):
                print("Invalid song ID")  
                self.fields['song'].queryset = Song.objects.none()
        else:
            self.fields['song'].queryset = Song.objects.none()
