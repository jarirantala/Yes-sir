package com.example.yessir.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.yessir.R
import com.example.yessir.model.HistoryItem
import com.example.yessir.constants.IntentTypes

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ListItemsScreen(
    viewModel: VoiceViewModel,
    initialTab: Int = 0,
    onMenuClick: () -> Unit
) {
    var selectedTab by remember(initialTab) { mutableStateOf(initialTab) }
    val tabs = listOf(stringResource(R.string.tab_todos), stringResource(R.string.tab_notes))
    
    val todoItems by viewModel.todoItems.collectAsState()
    val noteItems by viewModel.noteItems.collectAsState()
    val historyItemsList = if (selectedTab == 0) todoItems else noteItems
    
    val isLoading by viewModel.isHistoryLoading.collectAsState()

    val historyError by viewModel.historyError.collectAsState()

    LaunchedEffect(selectedTab) {
        if (selectedTab == 0) viewModel.loadTodosIfNeeded()
        else viewModel.loadNotesIfNeeded()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.title_history)) },
                navigationIcon = {
                    IconButton(onClick = onMenuClick) {
                        Icon(Icons.Default.Menu, contentDescription = stringResource(R.string.content_desc_menu))
                    }
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            TabRow(selectedTabIndex = selectedTab) {
                tabs.forEachIndexed { index, title ->
                    Tab(
                        selected = selectedTab == index,
                        onClick = { selectedTab = index },
                        text = { Text(title) }
                    )
                }
            }

            if (isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else if (historyError != null) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(text = historyError ?: "Unknown error", color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = {
                        viewModel.clearHistoryError()
                        if (selectedTab == 0) viewModel.loadTodosIfNeeded()
                        else viewModel.loadNotesIfNeeded()
                    }) {
                        Text("Retry")
                    }
                }
            } else if (historyItemsList.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text(stringResource(R.string.empty_list))
                }
            } else {
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(items = historyItemsList) { item ->
                        ListItem(
                            headlineContent = { Text(item.text ?: item.title ?: "") },
                            supportingContent = { 
                                item.created_at?.let { Text(formatTimestamp(it)) }
                            },
                            trailingContent = {
                                IconButton(onClick = { 
                                    viewModel.deleteItem(item.id, if (selectedTab == 0) IntentTypes.TODO else IntentTypes.NOTE) 
                                }) {
                                    Icon(Icons.Default.Delete, contentDescription = "Delete")
                                }
                            },
                            modifier = Modifier.padding(vertical = 4.dp)
                        )
                        HorizontalDivider()
                    }
                }
            }
        }
    }
}

private fun formatTimestamp(isoString: String): String {
    return try {
        // Backend sends UTC ISO8601 (often naive)
        // e.g. 2024-02-08T12:00:00.000000
        val parsed = java.time.LocalDateTime.parse(isoString)
        val formatter = java.time.format.DateTimeFormatter.ofPattern("dd-MM-yyyy HH.mm")
        parsed.format(formatter)
    } catch (e: Exception) {
        isoString
    }
}
