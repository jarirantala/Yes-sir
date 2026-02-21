package com.example.yessir.di

import android.app.Application
import com.example.yessir.media.AudioRecorder
import com.example.yessir.model.VoiceRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideVoiceRepository(): VoiceRepository {
        return VoiceRepository()
    }

    @Provides
    @Singleton
    fun provideAudioRecorder(app: Application): AudioRecorder {
        return AudioRecorder(app)
    }
}
